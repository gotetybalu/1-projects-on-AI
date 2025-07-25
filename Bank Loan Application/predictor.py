import pandas as pd
def calculate_financial_ratios(data_row):
    gross_income = data_row['Gross Income']
    existing_loan_amount = data_row['Existing loan amount']
    debit = data_row['debit']
    bank_credit = data_row['Bank credit']
    dti = existing_loan_amount / gross_income if gross_income > 0 else float('inf')
    expense_ratio = debit / bank_credit if bank_credit > 0 else float('inf')
    disposable_income = gross_income - (debit + data_row['Tax Payble'])
    return dti, expense_ratio, disposable_income

def predict_and_reason(user_data_dict, model, label_encoder, feature_columns):
    new_user_df = pd.DataFrame(user_data_dict)

    # Ensure columns are in the right order and complete
    new_user_df = new_user_df.reindex(columns=feature_columns)

    if new_user_df.isnull().any().any():
        missing_cols = new_user_df.columns[new_user_df.isnull().any()]
        raise ValueError(f"Missing columns in input data: {list(missing_cols)}")

    predicted_encoded = model.predict(new_user_df)
    predicted_status = label_encoder.inverse_transform(predicted_encoded)[0]

    gross_income = new_user_df['Gross Income'].iloc[0]
    existing_loan_amount = new_user_df['Existing loan amount'].iloc[0]
    assets = new_user_df['Assets'].iloc[0]
    years_experience = new_user_df['Years of experiance'].iloc[0]
    tax_payable = new_user_df['Tax Payble'].iloc[0]
    debit = new_user_df['debit'].iloc[0]
    bank_credit = new_user_df['Bank credit'].iloc[0]

    dti, expense_ratio, disposable_income = calculate_financial_ratios(new_user_df.iloc[0])

    DTI_THRESHOLD_REJECT = 0.40
    MIN_GROSS_INCOME_APPROVE = 70000
    MAX_EXISTING_LOAN_REJECT = 500000
    MIN_ASSETS_APPROVE = 100000
    MIN_YEARS_EXPERIENCE_APPROVE = 5
    MAX_EXPENSE_RATIO_REJECT = 0.50
    
    reason_parts = []

    if predicted_status == 'Rejected':
        if dti > DTI_THRESHOLD_REJECT:
            reason_parts.append(f"Debt-to-income ratio ({dti:.2f}) exceeds maximum allowed ({DTI_THRESHOLD_REJECT:.2f}).\n")
        if gross_income < MIN_GROSS_INCOME_APPROVE * 0.8:
            reason_parts.append(f"Gross Income ({gross_income:,.0f}) is lower than typical approval requirements.\n")
        if existing_loan_amount > MAX_EXISTING_LOAN_REJECT:
            reason_parts.append(f"Existing loan amount ({existing_loan_amount:,.0f}) is considerably high.\n")
        if assets < MIN_ASSETS_APPROVE * 0.5:
            reason_parts.append(f"Assets (${assets:,.0f}) are insufficient.\n")
        if expense_ratio > MAX_EXPENSE_RATIO_REJECT:
            reason_parts.append(f"Expense Ratio ({expense_ratio:.2f}) is unfavorable.\n")
        if len(reason_parts) == 1:
            reason_parts.append("The application does not meet the general criteria for approval. Please review the financial details.\n")
            
    else:  # Approved
        if gross_income >= MIN_GROSS_INCOME_APPROVE:
            reason_parts.append(f"Gross Income ({gross_income:,.0f}) meets requirements.\n")
        if disposable_income > 0.3 * gross_income:
            reason_parts.append(f"Disposable Income ({disposable_income:,.0f}) is strong.\n")
        if dti <= DTI_THRESHOLD_REJECT:
            reason_parts.append(f"DTI ({dti:.2f}) is healthy.\n")
        if expense_ratio <= MAX_EXPENSE_RATIO_REJECT:
            reason_parts.append(f"Expense Ratio ({expense_ratio:.2f}) is favorable.\n")
        if years_experience >= MIN_YEARS_EXPERIENCE_APPROVE:
            reason_parts.append(f"Years of experience ({years_experience}) provides stability.\n")
        if assets >= MIN_ASSETS_APPROVE:
            reason_parts.append(f"Substantial assets ({assets:,.0f}) provide additional financial strength.\n")
        elif assets > 0:
            reason_parts.append(f"Assets ({assets:,.0f}) contribute to financial health.\n")
        if len(reason_parts) == 1:
            reason_parts.append("The application meets the general criteria for approval.\n")

    return predicted_status, " ".join(reason_parts), new_user_df
