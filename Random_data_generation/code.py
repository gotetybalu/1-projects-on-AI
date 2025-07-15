import pandas as pd
import numpy as np
import os # Import the os module to handle directory creation

# Set a seed for reproducibility
np.random.seed(42)

def generate_financial_data(num_records=100):
    
    data = {}

    # Candidate ID - unique identifier for each record
    # Generates IDs like 'CAND0001', 'CAND0002', up to 'CAND5000' for 5000 records
    data['Candidate ID'] = [f'CAND{i+1:04d}' for i in range(num_records)]

    # Basic Salary - realistic range (minimum 50,000)
    data['Basic'] = np.random.randint(50000, 150000, num_records)

    # Conveyance - typically a percentage of basic or fixed
    data['Conveyance'] = np.round(data['Basic'] * np.random.uniform(0.05, 0.1), 0)

    # HRA (House Rent Allowance) - typically 40-50% of basic in non-metros, higher in metros
    data['HRA'] = np.round(data['Basic'] * np.random.uniform(0.3, 0.5), 0)

    # Gross Income calculation (initial estimate)
    # Adds a small random component to make it less directly dependent on Basic, Conveyance, HRA
    data['Gross Income'] = data['Basic'] + data['Conveyance'] + data['HRA'] + np.random.randint(0, 15000, num_records)

    # Income from other sources (e.g., freelance, interest)
    other_income_values = np.random.uniform(0, 50000, num_records)
    # 40% of records will have zero 'Income from other sources' for diversity
    zero_mask = np.random.choice([True, False], size=num_records, p=[0.4, 0.6])
    data['Income from other sources'] = np.where(zero_mask, 0, np.round(other_income_values, 0))

    # Total Income (Gross Income + Income from other sources)
    total_income = data['Gross Income'] + data['Income from other sources']

    # Bank Credit (Total income should roughly align with bank credits + a small buffer)
    # Simulates bank deposits slightly higher than total income
    data['Bank credit'] = total_income + np.random.randint(1000, 5000, num_records)

    # Debit - expenses, EMIs, etc.
    data['debit'] = np.round(total_income * np.random.uniform(0.3, 0.8), 0)
    # Ensures debit does not exceed total income (adjusted to 90% of total income if it does)
    data['debit'][data['debit'] >= total_income] = total_income[data['debit'] >= total_income] * 0.9

    # Years of Experience
    data['Years of experiance'] = np.random.randint(0, 20, num_records)

    # Existing loan amount - some people won't have loans
    existing_loan_values = np.random.uniform(0, 1500000, num_records)
    # 50% of records will have zero 'Existing loan amount'
    zero_loan_mask = np.random.choice([True, False], size=num_records, p=[0.5, 0.5])
    data['Existing loan amount'] = np.where(zero_loan_mask, 0, np.round(existing_loan_values, 0))

    # Assets - New column for liquid/fixed assets
    asset_values = np.random.uniform(10000, 5000000, num_records) # Range from 10K to 5M
    # 30% will have lower/zero assets for diversity
    low_asset_mask = np.random.choice([True, False], size=num_records, p=[0.3, 0.7])
    data['Assets'] = np.where(low_asset_mask, np.random.uniform(0, 100000, num_records), np.round(asset_values, 0))
    data['Assets'] = np.round(data['Assets'], 0) # Round to nearest whole number

    # Regime (Old or New Tax Regime)
    data['Regime'] = np.random.choice(['Old', 'New'], num_records)

    # Tax Payable - simplified calculation based on regime
    tax_factor_old = np.random.uniform(0.05, 0.2)
    tax_factor_new = np.random.uniform(0.1, 0.25)
    data['Tax Payble'] = np.where(
        data['Regime'] == 'Old',
        np.round(data['Gross Income'] * tax_factor_old, 0),
        np.round(data['Gross Income'] * tax_factor_new, 0)
    )
    data['Tax Payble'][data['Tax Payble'] < 0] = 0 # Ensure tax payable is not negative

    df = pd.DataFrame(data)

    # Calculate Key Financial Ratios/Metrics
    df['Disposable Income'] = df['Gross Income'] + df['Income from other sources'] - df['Tax Payble'] - df['debit']

    # Debt-to-Income Ratio (DTI) - Existing loan burden relative to total income
    df['DTI'] = df['Existing loan amount'] / (df['Gross Income'] + df['Income from other sources'])
    # Handle division by zero for DTI if total income is zero
    df.loc[(df['Gross Income'] + df['Income from other sources']) == 0, 'DTI'] = 0

    # Expense Ratio (ER) - Debits relative to Bank Credit (or total income)
    df['Expense Ratio'] = df['debit'] / df['Bank credit']
    # Handle division by zero for Expense Ratio if bank credit is zero
    df.loc[df['Bank credit'] == 0, 'Expense Ratio'] = 1.0 # Set to 1.0 if no bank credit

    # Loan Approval Logic
    df['Loan Approved status'] = 'Rejected'
    df['Reason for approval or rejected'] = ''

    # Define Thresholds (These are illustrative and should be set based on business rules)
    MIN_GROSS_INCOME_FOR_LOAN = 40000
    MIN_DISPOSABLE_INCOME_THRESHOLD = 7000
    MAX_DTI_THRESHOLD = 0.40
    MAX_EXPENSE_RATIO_THRESHOLD = 0.75
    MIN_YEARS_EXPERIENCE_FOR_APPROVAL = 2
    HIGH_EXISTING_LOAN_AMOUNT_THRESHOLD = 1000000
    SUBSTANTIAL_ASSETS_THRESHOLD = 500000 # Assets above this amount are considered substantial

    for i in range(num_records):
        disposable_income = df.loc[i, 'Disposable Income']
        dti = df.loc[i, 'DTI']
        years_exp = df.loc[i, 'Years of experiance']
        gross_income = df.loc[i, 'Gross Income']
        existing_loan = df.loc[i, 'Existing loan amount']
        expense_ratio = df.loc[i, 'Expense Ratio']
        assets = df.loc[i, 'Assets'] # Get the new Assets value
        candidate_id = df.loc[i, 'Candidate ID']

        rejection_reasons = []
        approval_factors = []

        # --- REJECTION CRITERIA (Hard Stops) ---

        # 1. Gross Income Check
        if gross_income < MIN_GROSS_INCOME_FOR_LOAN:
            rejection_reasons.append(f"Gross income (${gross_income:,.0f}) is below the minimum required (${MIN_GROSS_INCOME_FOR_LOAN:,.0f}).")

        # 2. Disposable Income Check
        if disposable_income < MIN_DISPOSABLE_INCOME_THRESHOLD:
            rejection_reasons.append(f"Disposable income (${disposable_income:,.0f}) is insufficient, below minimum required (${MIN_DISPOSABLE_INCOME_THRESHOLD:,.0f}).")

        # 3. Debt-to-Income Ratio Check
        if dti > MAX_DTI_THRESHOLD:
            rejection_reasons.append(f"Debt-to-income ratio ({dti:.2f}) exceeds maximum allowed ({MAX_DTI_THRESHOLD:.2f}).")
        elif existing_loan > HIGH_EXISTING_LOAN_AMOUNT_THRESHOLD:
            rejection_reasons.append(f"Existing loan amount (${existing_loan:,.0f}) is exceptionally high.")

        # 4. Expense Ratio Check
        if expense_ratio > MAX_EXPENSE_RATIO_THRESHOLD:
            rejection_reasons.append(f"Expense ratio ({expense_ratio:.2f}) is too high, indicating high spending relative to income.")

        # 5. Years of Experience Check
        if years_exp < MIN_YEARS_EXPERIENCE_FOR_APPROVAL:
            rejection_reasons.append(f"Years of experience ({years_exp}) is below the recommended minimum ({MIN_YEARS_EXPERIENCE_FOR_APPROVAL}).")


        # --- DETERMINE APPROVAL STATUS AND REASON ---

        if rejection_reasons:
            df.loc[i, 'Loan Approved status'] = 'Rejected'
            df.loc[i, 'Reason for approval or rejected'] = f"For Candidate ID {candidate_id}: " + "; ".join(rejection_reasons)
        else:
            df.loc[i, 'Loan Approved status'] = 'Approved'
            # Construct a comprehensive approval reason
            approval_factors.append(f"Gross Income (${gross_income:,.0f}) meets requirements.")
            approval_factors.append(f"Disposable Income (${disposable_income:,.0f}) is strong.")
            approval_factors.append(f"DTI ({dti:.2f}) is healthy.")
            approval_factors.append(f"Expense Ratio ({expense_ratio:.2f}) is favorable.")
            approval_factors.append(f"Years of experience ({years_exp}) provides stability.")
            if assets >= SUBSTANTIAL_ASSETS_THRESHOLD:
                approval_factors.append(f"Substantial assets (${assets:,.0f}) provide additional financial strength.")
            elif assets > 0: # If assets are present but not substantial
                approval_factors.append(f"Assets (${assets:,.0f}) contribute to financial health.")

            df.loc[i, 'Reason for approval or rejected'] = f"For Candidate ID {candidate_id}: Approved. " + "; ".join(approval_factors)

    # Clean up temporary columns used for calculations
    df = df.drop(columns=['Disposable Income', 'DTI', 'Expense Ratio'])

    return df

# Generate 5000 records
df = generate_financial_data(num_records=5000)

# Define the full path for the Excel file
excel_file_name = r'D:\\Datasets\\5k_dummy_records.xlsx' # Raw string to handle backslashes

# Ensure the directory exists before saving the file
output_directory = os.path.dirname(excel_file_name)
if not os.path.exists(output_directory):
    os.makedirs(output_directory)
    print(f"Created directory: {output_directory}")

# Save the DataFrame to an Excel file
df.to_excel(excel_file_name, index=False, sheet_name='Loan Applicants')

print(f"\nData successfully saved to '{excel_file_name}' with 5000 records.")

# Display the first few rows of the DataFrame (including the new Assets column)
print("First 5 rows of the generated DataFrame:")
print(df.head())

# Display some statistics to check the data distribution
print("\nDataFrame Info:")
df.info()

print("\nDescriptive Statistics:")
print(df.describe())

print("\nValue Counts for Loan Approved Status:")
print(df['Loan Approved status'].value_counts())

print("\nSample Reasons for Approval/Rejection (with Candidate ID):")
# Display 10 random samples from the larger dataset
print(df[['Candidate ID', 'Loan Approved status', 'Reason for approval or rejected']].sample(10))
