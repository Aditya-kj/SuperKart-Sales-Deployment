import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Predictor")

# Load the serialized model pipeline (which includes our scaler and encoder)
model = joblib.load("superkart_model.joblib")

def preprocess_incoming_data(df):
    """
    This function acts as a safety net. If a user uploads the raw CSV (with Store_Establishment_Year 
    instead of Store_Age_Years), this function dynamically performs the same feature engineering 
    we did in Section 1 and 2 before passing the data to the model.
    """
    df = df.copy()
    
    # 1. Product_Id_char
    if 'Product_Id' in df.columns and 'Product_Id_char' not in df.columns:
        df['Product_Id_char'] = df['Product_Id'].astype(str).str[:2]
        
    # 2. Store_Age_Years
    if 'Store_Establishment_Year' in df.columns and 'Store_Age_Years' not in df.columns:
        df['Store_Age_Years'] = 2026 - df['Store_Establishment_Year']
        
    # 3. Product_Type_Category
    if 'Product_Type' in df.columns and 'Product_Type_Category' not in df.columns:
        perishables = ['Dairy', 'Meat', 'Fruits and Vegetables', 'Breakfast', 'Breads', 'Seafood']
        df['Product_Type_Category'] = df['Product_Type'].apply(
            lambda x: 'Perishables' if x in perishables else 'Non Perishables'
        )
        
    # 4. Data Cleaning
    if 'Product_Sugar_Content' in df.columns:
        df['Product_Sugar_Content'] = df['Product_Sugar_Content'].replace('reg', 'Regular')
        
    # 5. Drop raw columns to match the trained model's expected features
    cols_to_drop = [c for c in ['Product_Id', 'Store_Establishment_Year', 'Product_Type'] if c in df.columns]
    if cols_to_drop:
        df = df.drop(cols_to_drop, axis=1)
        
    return df

# Define a root endpoint for basic health checks
@superkart_api.get('/')
def home():
    return "Welcome to the SuperKart Sales Prediction API!"

# Define the endpoint for online (single) prediction
@superkart_api.post('/v1/predict')
def predict_sales():
    data = request.get_json()
    input_df = pd.DataFrame([data])
    
    # Apply our safety-net feature engineering
    processed_df = preprocess_incoming_data(input_df)
    
    # Generate prediction using the pipeline
    prediction = model.predict(processed_df)[0]
    return jsonify({'Predicted_Sales': round(float(prediction), 2)})

# Define the endpoint for batch prediction via CSV
@superkart_api.post('/v1/predictbatch')
def predict_sales_batch():
    file = request.files['file']
    input_df = pd.read_csv(file)
    
    # Apply our safety-net feature engineering to the whole batch
    processed_df = preprocess_incoming_data(input_df)
    
    # Generate predictions
    predictions = model.predict(processed_df).tolist()
    
    # Map predictions to their row index in a dictionary
    output_dict = {str(i): round(float(pred), 2) for i, pred in enumerate(predictions)}
    return jsonify(output_dict)

if __name__ == '__main__':
    superkart_api.run(debug=True, host='0.0.0.0', port=7860)
