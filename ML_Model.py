import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

df = pd.read_csv('augmented_traffic_data.csv')

required_columns = ['RoadID', 'TimeOfDay', 'Capacity', 'Volume', 'C']
if not all(col in df.columns for col in required_columns):
    print(f"File should contain: {required_columns}")
else:
    le_road = LabelEncoder()
    le_time = LabelEncoder()
    df['Road_ID_Encoded'] = le_road.fit_transform(df['RoadID'])
    df['Time_Encoded'] = le_time.fit_transform(df['TimeOfDay'])

    X = df[['Road_ID_Encoded', 'Time_Encoded', 'Capacity', 'Volume']]
    y = df['C']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred):.4f}")
    print(f"R-squared Score: {r2_score(y_test, y_pred):.4f}")

    # Save the model and encoders
    joblib.dump(model, 'traffic_model.pkl')
    joblib.dump(le_road, 'road_encoder.pkl')
    joblib.dump(le_time, 'time_encoder.pkl')
    print("Model and encoders saved successfully.")

def predict_traffic(RoadID, TimeOfDay, Capacity, Volume):
    """
    Predict traffic congestion (C) for given inputs.
    
    Parameters:
    RoadID (str): Road identifier
    TimeOfDay (str): Time period (e.g., 'Morning', 'Afternoon', etc.)
    Capacity (int): Road capacity
    Volume (int): Traffic volume
    
    Returns:
    float: Predicted congestion value
    """
    # Load the model and encoders
    model = joblib.load('traffic_model.pkl')
    le_road = joblib.load('road_encoder.pkl')
    le_time = joblib.load('time_encoder.pkl')
    
    # Encode categorical variables
    try:
        road_encoded = le_road.transform([RoadID])[0]
        time_encoded = le_time.transform([TimeOfDay])[0]
    except ValueError as e:
        print(f"Error encoding inputs: {e}")
        return None
    
    # Create input array
    input_data = [[road_encoded, time_encoded, Capacity, Volume]]
    
    # Make prediction
    prediction = model.predict(input_data)[0]
    return prediction

# Example usage
if __name__ == "__main__":
    # Sample prediction
    sample_prediction = predict_traffic('Road1', 'Morning', 1000, 500)
    if sample_prediction is not None:
        print(f"Sample prediction for Road1, Morning, Capacity=1000, Volume=500: {sample_prediction:.4f}")