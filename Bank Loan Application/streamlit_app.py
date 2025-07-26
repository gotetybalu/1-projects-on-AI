import streamlit as st
import pandas as pd
import joblib
from predictor import predict_and_reason
from from_excel import extract_row_as_dict
from data_utils import load_loan_data
from preprocessing import prepare_features
from train import train_model
import os

st.set_page_config(page_title="Loan Approval Predictor", layout="centered")
st.title("🏦 Loan Approval Predictor")

st.markdown("Upload an Excel file containing loan applicant data:")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file:
    sheet = st.text_input("Sheet Name", value="Sheet1")
    index = st.number_input("Row Index (0-based)", min_value=0, value=0)
    if st.button("Predict Loan Status"):
        try:
            columns_to_extract = ['Candidate ID','Basic', 'Conveyance', 'HRA', 'Gross Income',
                                  'Income from other sources','Bank credit','debit',
                                  'Years of experiance','Existing loan amount','Assets',
                                  'Regime','Tax Payble']
            input_dict = extract_row_as_dict(uploaded_file, sheet, index, columns_to_extract)
            
            # Load model pipeline if exists
            model_file = "trained_model.pkl"
            if os.path.exists(model_file) and os.path.exists("label_encoder.pkl"):
                model = joblib.load(model_file)
                label_encoder = joblib.load("label_encoder.pkl")
            else:
                st.warning("Training model from default dataset...")
                df = load_loan_data("D:\\Datasets\\5k_dummy_records.xlsx", "Loan Applicants")
                X, y_encoded, preprocessor, label_encoder, num_cols, cat_cols, feature_cols = prepare_features(df)
                model, _, _ = train_model(X, y_encoded, preprocessor)
                joblib.dump(model, model_file)
                joblib.dump(label_encoder, "label_encoder.pkl")
            
            # Get feature columns for ordering
            feature_columns = ['Candidate ID','Basic', 'Conveyance', 'HRA', 'Gross Income',
                               'Income from other sources','Bank credit','debit',
                               'Years of experiance','Existing loan amount','Assets',
                               'Regime','Tax Payble']

            status, reason, _ = predict_and_reason(input_dict, model, label_encoder, feature_columns)
            st.success(f"Loan Status: {status}")
            st.info(reason)

        except Exception as e:
            st.error(f"Error: {e}")
