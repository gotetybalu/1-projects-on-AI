from data_utils import load_loan_data
from preprocessing import prepare_features
from train import train_model, evaluate_model, get_feature_importances
from predictor import predict_and_reason
from from_excel import extract_row_as_dict
def main():   
    file_path = r'D:\\Datasets\\5k_dummy_records.xlsx'
    sheet_name = 'Loan Applicants'
    target_column = 'Loan Approved status'

    df = load_loan_data(file_path, sheet_name)

    X, y_encoded, preprocessor, le, numerical_features, categorical_features, feature_columns = prepare_features(df, target_column)

    model, X_test, y_test = train_model(X, y_encoded, preprocessor)
    evaluate_model(model, X_test, y_test, le)
    get_feature_importances(model, numerical_features, categorical_features)

    # Prepare new user input dictionary (example)

    file_path= r"D:\Datasets\testdata.xlsx"
    sheet_name = 'Sheet1'
    columns_to_extract = ['Candidate ID','Basic', 'Conveyance', 'HRA', 'Gross Income','Income from other sources',
                      'Bank credit','debit','Years of experiance','Existing loan amount','Assets','Regime','Tax Payble']
    user_input=int(input("option"))
    if(user_input==1):
        new_user_data_1 = extract_row_as_dict(file_path, sheet_name, 0, columns_to_extract)
        status, reason, user_df = predict_and_reason(new_user_data_1, model, le, feature_columns)
        print("\nNew user data for prediction:")
        print(user_df)
        print(f"\nPredicted Loan Approval Status: {status}")
        print(f"Reason: {reason}")
if __name__ == "__main__":
    main()
