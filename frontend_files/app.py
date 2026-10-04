import streamlit as st
import requests
import pandas as pd

# Define the backend Flask API URL (defaults to localhost port 7860)
BACKEND_URL = "http://127.0.0.1:7860"

st.set_page_config(page_title="SuperKart Forecaster", layout="wide")
st.title("🛒 SuperKart Sales Forecasting App")
st.write("Use this portal to forecast sales for a single product or run batch predictions.")

# Create tabs for Single Prediction and Batch Prediction
tab1, tab2 = st.tabs(["Single Prediction", "Batch Prediction"])

# --- TAB 1: SINGLE PREDICTION ---
with tab1:
    st.header("Single Product Inference")
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_id = st.text_input("Product ID", value="FDX07")
            product_weight = st.number_input("Product Weight", min_value=1.0, value=12.5)
            product_sugar = st.selectbox("Sugar Content", ["Regular", "Low Sugar", "No Sugar", "reg"])
            product_area = st.number_input("Allocated Area Ratio", min_value=0.0, max_value=1.0, value=0.05)
            product_type = st.selectbox("Product Type", ["Dairy", "Meat", "Snack Foods", "Household", "Fruits and Vegetables"])
            product_mrp = st.number_input("Product MRP", min_value=10.0, value=150.0)
            
        with col2:
            store_id = st.text_input("Store ID", value="OUT049")
            store_est_year = st.number_input("Establishment Year", min_value=1980, max_value=2026, value=1999)
            store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
            store_city = st.selectbox("City Tier", ["Tier 1", "Tier 2", "Tier 3"])
            store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])
            
        submit = st.form_submit_button("Predict Sales")

    if submit:
        # Build the JSON payload matching raw data column names
        payload = {
            "Product_Id": product_id,
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar,
            "Product_Allocated_Area": product_area,
            "Product_Type": product_type,
            "Product_MRP": product_mrp,
            "Store_Id": store_id,
            "Store_Establishment_Year": store_est_year,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_city,
            "Store_Type": store_type
        }
        
        try:
            # Send POST request to Flask backend
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload)
            if response.status_code == 200:
                prediction = response.json().get("Predicted_Sales")
                st.success(f"📈 Predicted Total Sales: **${prediction}**")
            else:
                st.error("Error from backend API. Make sure the Flask server is running.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the backend. Is Flask running on port 7860?")

# --- TAB 2: BATCH PREDICTION ---
with tab2:
    st.header("Batch Inference via CSV")
    uploaded_file = st.file_uploader("Upload SuperKart_batch_data.csv", type=["csv"])
    
    if uploaded_file is not None:
        st.write("File uploaded successfully! Click below to generate predictions.")
        if st.button("Run Batch Inference"):
            try:
                # Send the CSV file to the Flask backend
                files = {"file": uploaded_file.getvalue()}
                response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files)
                
                if response.status_code == 200:
                    predictions_dict = response.json()
                    # Convert the returned JSON dictionary into a DataFrame for easy viewing
                    results_df = pd.DataFrame(list(predictions_dict.items()), columns=['Row_Index', 'Predicted_Sales'])
                    st.success("Batch predictions generated successfully!")
                    st.dataframe(results_df)
                else:
                    st.error("Error processing batch file.")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend.")
