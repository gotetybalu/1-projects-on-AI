import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import numpy as np
import warnings
import os # Import os module for path checking

# Suppress warnings for cleaner output, especially for Logistic Regression with small data
warnings.filterwarnings('ignore')

# --- Load data from Excel file ---
# IMPORTANT: This path 'D:\Datasets\5k_dummy_records.xlsx' is specific to your local machine.
# For this code to run, the file must exist at this exact path in the environment where the script is executed.
file_path = "D:\\Datasets\\5k_dummy_records.xlsx"

try:
    # Check if the file exists before attempting to read
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'. Please ensure the file exists.")
        # As a fallback, we'll use the original dummy data if the file isn't found.
        # In a real scenario, you might want to exit or raise an error.
        print("Falling back to dummy data for demonstration.")
        test_data = {
            'Basic': [80000, 45000, 120000, 70000],
            'Conveyance': [8000, 4500, 12000, 7000],
            'HRA': [32000, 18000, 48000, 28000],
            'Gross Income': [120000, 67500, 180000, 105000],
            'Income from other sources': [10000, 0, 25000, 5000],
            'Bank credit': [135000, 70000, 210000, 115000],
            'debit': [30000, 50000, 40000, 80000],
            'Years of experiance': [10, 1, 15, 3],
            'Existing loan amount': [50000, 800000, 0, 150000],
            'Assets': [700000, 50000, 2000000, 100000],
            'Regime': ['Old', 'New', 'Old', 'New'],
            'Loan Approved': [1, 0, 1, 0]
        }
        df = pd.DataFrame(test_data)
    else:
        df = pd.read_excel(file_path)
        print(f"Successfully loaded data from '{file_path}'.")

except Exception as e:
    print(f"An error occurred while loading the Excel file: {e}")
    print("Falling back to dummy data for demonstration.")
    test_data = {
        'Basic': [80000, 45000, 120000, 70000],
        'Conveyance': [8000, 4500, 12000, 7000],
        'HRA': [32000, 18000, 48000, 28000],
        'Gross Income': [120000, 67500, 180000, 105000],
        'Income from other sources': [10000, 0, 25000, 5000],
        'Bank credit': [135000, 70000, 210000, 115000],
        'debit': [30000, 50000, 40000, 80000],
        'Years of experiance': [10, 1, 15, 3],
        'Existing loan amount': [50000, 800000, 0, 150000],
        'Assets': [700000, 50000, 2000000, 100000],
        'Regime': ['Old', 'New', 'Old', 'New'],
        'Loan Approved': [1, 0, 1, 0]
    }
    df = pd.DataFrame(test_data)


print("Original DataFrame (first 5 rows if large):")
print(df.head())
print("\n" + "="*50 + "\n")

# Separate features (X) and new target (y_loan_approved)
# 'Loan Approved' is our new target variable. Ensure this column exists in your Excel file.
if 'Loan Approved' not in df.columns:
    print("Error: 'Loan Approved' column not found in the loaded data. Please check your Excel file.")
    # Exit or handle this error appropriately
    exit() # Exiting for demonstration, in a real app you might handle differently
y_loan_approved = df['Loan Approved']
X = df.drop('Loan Approved', axis=1)


# Preprocessing: Convert categorical 'Regime' column into numerical using one-hot encoding
# Ensure 'Regime' column exists in your Excel file
if 'Regime' in X.columns:
    X = pd.get_dummies(X, columns=['Regime'], drop_first=True)
else:
    print("Warning: 'Regime' column not found in features. Skipping one-hot encoding for 'Regime'.")


print("Features (X) after one-hot encoding (first 5 rows if large):")
print(X.head())
print("\n" + "="*50 + "\n")

print("Categorical Target (y_loan_approved) (first 5 values if large):")
print(y_loan_approved.head())
print("\n" + "="*50 + "\n")

# Split the data into training and testing sets
# Stratify ensures that each split has roughly the same proportion of target categories as the full dataset.
# Adjust test_size based on the actual size of your 5k dataset. A 0.2 (20%) test size is common.
X_train, X_test, y_train, y_test = train_test_split(X, y_loan_approved, test_size=0.2, random_state=42, stratify=y_loan_approved)

print(f"Training data shape: {X_train.shape}")
print(f"Testing data shape: {X_test.shape}")
print("\n" + "="*50 + "\n")

# --- Initialize and train different Classification models ---

models = {
    "RandomForestClassifier": RandomForestClassifier(n_estimators=100, random_state=42),
    "DecisionTreeClassifier": DecisionTreeClassifier(random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42) # Increased max_iter for convergence
}

for name, model in models.items():
    print(f"--- Training {name} ---")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print(f"Predictions for {name} on test set (first 5 if large):")
    print(f"Actual Loan Approved (y_test): {y_test.head().tolist()}")
    print(f"Predicted Loan Approved (y_pred): {y_pred[:5].tolist()}") # Show first 5 predictions
    print("\n" + "="*20 + "\n")

    # Evaluate the model's performance
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Evaluation for {name}:")
    print(f"Accuracy: {accuracy:.2f}")
    try:
        # For binary classification, precision, recall, f1-score are calculated for the positive class (1)
        print(f"Classification Report:\n{classification_report(y_test, y_pred, zero_division=0)}")
    except ValueError as e:
        print(f"Could not generate full classification report due to: {e}.")

    print("\n" + "="*50 + "\n")

# --- Example of making a prediction for a new data point using RandomForestClassifier ---
print("Demonstrating prediction for a new data point using RandomForestClassifier:")

# Create a new data point (example values).
# Ensure all feature columns used during training are present, even if their values are 0.
# The 'Regime_New' column is created by one-hot encoding.
new_data_point = pd.DataFrame({
    'Basic': [90000],
    'Conveyance': [9000],
    'HRA': [36000],
    'Gross Income': [135000],
    'Income from other sources': [5000],
    'Bank credit': [140000],
    'debit': [35000],
    'Years of experiance': [5],
    'Existing loan amount': [100000],
    'Assets': [800000],
    'Regime_New': [1] # Assuming 'New' regime for this example (1 for New, 0 for Old)
}, index=[0])

# Ensure the columns of the new data point match the columns used for training
# This is crucial if your training data from Excel has different columns or order.
# For robust prediction, you should align columns.
# Example of aligning columns (uncomment if needed):
# new_data_point = new_data_point.reindex(columns=X_train.columns, fill_value=0)


print("New data point for prediction (features):")
print(new_data_point)
print("\n" + "="*50 + "\n")

# Predict the 'Loan Approved' status for the new data point using the trained RandomForestClassifier
rf_model = models["RandomForestClassifier"]
predicted_loan_status = rf_model.predict(new_data_point)

print(f"Predicted Loan Approved status for the new data point: {'Approved' if predicted_loan_status[0] == 1 else 'Not Approved'}")
