"""ML traffic-congestion prediction module.

Trains (or loads) a Random Forest regressor that predicts a congestion factor
``C`` from ``(RoadID, TimeOfDay, Capacity, Volume)``.

- Run this file directly to (re)train and persist the model + encoders.
- Import :func:`predict_traffic`, :func:`predict_for_edge`, :func:`edge_to_road_id`,
  or :func:`is_available` from other modules to use the cached model at runtime
  without retraining.
"""

import os
from functools import lru_cache
from typing import Optional, Tuple

try:
    import joblib
except ImportError:  # pragma: no cover - handled at call sites
    joblib = None

_HERE = os.path.dirname(os.path.abspath(__file__))
_MODEL_PATH = os.path.join(_HERE, 'traffic_model.pkl')
_ROAD_ENC_PATH = os.path.join(_HERE, 'road_encoder.pkl')
_TIME_ENC_PATH = os.path.join(_HERE, 'time_encoder.pkl')
_CSV_PATH = os.path.join(_HERE, 'augmented_traffic_data.csv')

# The 8 hand-labeled roads in ``augmented_traffic_data.csv``. Mapping graph
# edges (sorted node-id tuple) to the human-friendly RoadID used in the CSV
# guarantees these roads keep their original ground-truth ``C`` values during
# training; every other graph edge gets an auto-generated RoadID below.
EDGE_TO_ROAD_NAME = {
    ("1", "3"): "Maadi-Downtown Road",
    ("1", "8"): "Maadi-Giza Road",
    ("2", "3"): "Nasr City-Downtown Road",
    ("2", "5"): "Nasr City-Heliopolis Road",
    ("3", "5"): "Downtown-Heliopolis Road",
    ("3", "6"): "Downtown-Zamalek Road",
    ("3", "9"): "Downtown-Mohandessin Road",
    ("3", "10"): "Downtown-Dokki Road",
}

# Time-period strings used by the trained LabelEncoder, in the same order the
# rest of the project uses for ``time_period`` ints (0=Morning ... 3=Night).
TIME_PERIODS = ['Morning', 'Afternoon', 'Evening', 'Night']


def _derive_road_id(node_a_name: str, node_b_name: str) -> str:
    """Produce a stable RoadID for a graph edge from its two node names."""
    return f"{node_a_name}-{node_b_name} Road"


@lru_cache(maxsize=1)
def _build_edge_road_map():
    """Map every graph edge -> a stable RoadID covering the whole network.

    Uses :data:`EDGE_TO_ROAD_NAME` for the 8 hand-labeled roads (preserving
    their original CSV names so real-world ``C`` values stay intact during
    training) and derives ``"<Node A>-<Node B> Road"`` for everything else.

    Returns ``dict[(str, str), str]`` keyed by sorted node-id tuples. Falls
    back to a copy of :data:`EDGE_TO_ROAD_NAME` if the graph cannot be loaded
    (e.g., when running this file in isolation).
    """
    try:
        from data_loader import load_data
        graph = load_data()
    except Exception:
        return dict(EDGE_TO_ROAD_NAME)

    result = dict(EDGE_TO_ROAD_NAME)
    for edge in graph.edges.values():
        a, b = sorted([edge.from_id, edge.to_id])
        if (a, b) in result:
            continue
        node_a = graph.nodes.get(a)
        node_b = graph.nodes.get(b)
        if node_a and node_b:
            result[(a, b)] = _derive_road_id(node_a.name, node_b.name)
    return result


@lru_cache(maxsize=1)
def _load():
    """Load (and cache) the model + encoders. Returns ``None`` if unavailable."""
    if joblib is None:
        return None
    if not (os.path.exists(_MODEL_PATH)
            and os.path.exists(_ROAD_ENC_PATH)
            and os.path.exists(_TIME_ENC_PATH)):
        return None
    try:
        return {
            'model': joblib.load(_MODEL_PATH),
            'road_enc': joblib.load(_ROAD_ENC_PATH),
            'time_enc': joblib.load(_TIME_ENC_PATH),
        }
    except Exception:
        return None


def is_available() -> bool:
    """``True`` iff joblib is installed and the trained artifacts can be loaded."""
    return _load() is not None


def supported_road_ids() -> Tuple[str, ...]:
    """Tuple of RoadID strings the model was trained on, or ``()`` if missing."""
    bundle = _load()
    if bundle is None:
        return ()
    return tuple(bundle['road_enc'].classes_)


def edge_to_road_id(from_id: str, to_id: str) -> Optional[str]:
    """Resolve a graph edge (by node ids) to a training-set RoadID.

    Returns a name for any edge in the graph after ``train_model()`` has
    expanded the dataset; falls back to the 8 hand-labeled roads if the
    graph isn't reachable.
    """
    return _build_edge_road_map().get(tuple(sorted([from_id, to_id])))


def predict_traffic(road_id: str, time_of_day: str,
                    capacity: int, volume: int) -> Optional[float]:
    """Predict the congestion factor ``C`` for a road at a given time period.

    Returns ``None`` if the model is unavailable or the inputs aren't covered
    by the trained encoders.
    """
    bundle = _load()
    if bundle is None:
        return None
    try:
        r = bundle['road_enc'].transform([road_id])[0]
        t = bundle['time_enc'].transform([time_of_day])[0]
    except ValueError:
        return None
    return float(bundle['model'].predict([[r, t, capacity, volume]])[0])


def predict_for_edge(edge, time_period: int = 0) -> Optional[float]:
    """Predict congestion for a graph ``Edge`` at a time-period int (0..3).

    Volume is approximated from the edge's stored ``traffic_pattern`` ratio
    (which encodes ``(volume / capacity) * 1.5`` clamped to [0.3, 2.5] in
    ``data_loader.py``), so the input distribution roughly matches training.
    """
    if not (0 <= time_period < len(TIME_PERIODS)):
        return None
    road_id = edge_to_road_id(edge.from_id, edge.to_id)
    if road_id is None:
        return None
    pattern = getattr(edge, 'traffic_pattern', [1.0, 0.7, 0.9, 0.5])
    ratio = pattern[time_period] if time_period < len(pattern) else 1.0
    estimated_volume = max(0, int(edge.capacity * (ratio / 1.5)))
    return predict_traffic(
        road_id,
        TIME_PERIODS[time_period],
        int(edge.capacity),
        estimated_volume,
    )


def congestion_label(c: float) -> str:
    """Human-readable label for a predicted congestion factor."""
    if c < 1.5:
        return "Light"
    if c < 2.3:
        return "Moderate"
    if c < 3.0:
        return "Heavy"
    return "Severe"


def _synthesize_rows_for_graph():
    """Generate one training row per (graph edge × time period).

    Volume is reverse-derived from the edge's ``traffic_pattern`` ratio
    (``data_loader.py`` stores ``clamp((volume / capacity) * 1.5, 0.3, 2.5)``)
    and the synthetic congestion target ``C`` follows a simple linear rule
    fit on the original ``augmented_traffic_data.csv``:
    ``C ≈ clamp(0.5 + 4.0 * (volume / capacity), 0.5, 3.5)``.

    Returns a ``list[dict]`` with the same columns as the CSV, or an empty
    list if the graph cannot be loaded.
    """
    try:
        from data_loader import load_data
        graph = load_data()
    except Exception:
        return []

    edge_map = _build_edge_road_map()
    rows = []
    for edge in graph.edges.values():
        key = tuple(sorted([edge.from_id, edge.to_id]))
        road_id = edge_map.get(key)
        if not road_id or edge.capacity <= 0:
            continue

        pattern = getattr(edge, 'traffic_pattern', [1.0, 0.7, 0.9, 0.5])
        for ti, period in enumerate(TIME_PERIODS):
            ratio = pattern[ti] if ti < len(pattern) else 1.0
            volume = max(0, int(edge.capacity * ratio / 1.5))
            vol_cap = volume / edge.capacity if edge.capacity else 0.0
            c = max(0.5, min(3.5, 0.5 + 4.0 * vol_cap))
            rows.append({
                'RoadID': road_id,
                'TimeOfDay': period,
                'Capacity': int(edge.capacity),
                'Volume': volume,
                'C': round(c, 2),
            })
    return rows


def train_model() -> dict:
    """(Re)train the Random Forest and persist the model + encoders.

    The training set is the **union** of two sources:

    1. ``augmented_traffic_data.csv`` — 32 hand-labeled rows for 8 central
       Cairo roads (kept as the source of truth for those edges).
    2. Synthetic rows generated from every other graph edge so predictions
       work for any route in the network.

    When a road appears in both sources the CSV row wins (its ``C`` value is
    real, not derived).

    Returns a result dict with the following keys:

        success: bool       — whether training completed and artifacts were saved
        message: str        — human-readable status / error message
        mse:     float      — mean squared error on the holdout (only if success)
        r2:      float      — R² score on the holdout (only if success)
        samples: int        — number of rows used for training (only if success)
        roads:   int        — distinct RoadIDs in the training set (only if success)

    Never raises for missing deps or bad inputs — always returns a dict.
    """
    if joblib is None:
        return {
            'success': False,
            'message': "joblib is not installed. Run: pip install -r requirements.txt",
        }

    try:
        import pandas as pd
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import LabelEncoder
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score
    except ImportError as e:
        return {
            'success': False,
            'message': (f"Missing ML dependency: {e}. "
                        "Run: pip install -r requirements.txt"),
        }

    if not os.path.exists(_CSV_PATH):
        return {
            'success': False,
            'message': f"Training CSV not found: {_CSV_PATH}",
        }

    try:
        df_csv = pd.read_csv(_CSV_PATH)

        required = ['RoadID', 'TimeOfDay', 'Capacity', 'Volume', 'C']
        missing = [c for c in required if c not in df_csv.columns]
        if missing:
            return {'success': False,
                    'message': f"CSV missing columns: {missing}"}

        # Refresh the cached graph map so the synthesizer picks up any
        # graph edits the user may have made between training runs.
        _build_edge_road_map.cache_clear()
        synthetic = _synthesize_rows_for_graph()

        if synthetic:
            df_extra = pd.DataFrame(synthetic, columns=required)
            # Concatenate CSV first, then synthetic, then drop duplicates
            # keeping the first occurrence so hand-labeled rows always win.
            df = pd.concat([df_csv, df_extra], ignore_index=True)
            df = df.drop_duplicates(
                subset=['RoadID', 'TimeOfDay'], keep='first'
            ).reset_index(drop=True)
        else:
            df = df_csv

        le_road = LabelEncoder()
        le_time = LabelEncoder()
        df['Road_ID_Encoded'] = le_road.fit_transform(df['RoadID'])
        df['Time_Encoded'] = le_time.fit_transform(df['TimeOfDay'])

        X = df[['Road_ID_Encoded', 'Time_Encoded', 'Capacity', 'Volume']]
        y = df['C']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mse = float(mean_squared_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))

        joblib.dump(model, _MODEL_PATH)
        joblib.dump(le_road, _ROAD_ENC_PATH)
        joblib.dump(le_time, _TIME_ENC_PATH)
        # Drop the cached old model so the next call to _load() re-reads from disk
        _load.cache_clear()

        return {
            'success': True,
            'message': "Training complete; model and encoders saved.",
            'mse': mse,
            'r2': r2,
            'samples': int(len(df)),
            'roads': int(df['RoadID'].nunique()),
        }
    except Exception as e:  # pragma: no cover - defensive
        return {'success': False, 'message': f"Training failed: {e}"}


if __name__ == "__main__":
    result = train_model()
    if result['success']:
        print(f"Mean Squared Error: {result['mse']:.4f}")
        print(f"R-squared Score:    {result['r2']:.4f}")
        print(f"Samples: {result['samples']}  Distinct roads: {result.get('roads', '?')}")
        print("Model and encoders saved.")

        sample = predict_traffic('Maadi-Downtown Road', 'Morning', 3000, 1500)
        if sample is not None:
            print(f"Sample prediction (Maadi-Downtown / Morning / 3000 / 1500): "
                  f"{sample:.4f} ({congestion_label(sample)})")
    else:
        print(f"Error: {result['message']}")
