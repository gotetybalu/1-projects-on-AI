import pandas as pd

def load_loan_data(file_path: str, sheet_name: str) -> pd.DataFrame:
    """Load dataset from Excel file."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        print("Dataset loaded successfully.")
        print(f"Dataset shape: {df.shape}")
        print("\nFirst 5 rows of the dataset:")
        print(df.head())
        print("\nDataset information:")
        df.info()
        return df
    except FileNotFoundError:
        print(f"Error: '{file_path}' not found.")
        raise
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        raise
