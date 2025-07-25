import pandas as pd

def extract_row_as_dict(file_path, sheet_name, row_index, columns):
    # Load Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    print("Columns in DataFrame:", df.columns.tolist())
    print("Columns requested:", columns)

    # Check columns exist in df
    missing_cols = [col for col in columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns missing in the sheet: {missing_cols}")

    row = df.loc[row_index, columns]

    # Convert each value from possible numpy types to native Python types
    feature_dict = {}
    for col in columns:
        val = row[col]
        # Convert numpy scalar to Python native type using item()
        if hasattr(val, 'item'):
            val = val.item()  # converts np.int64, np.float64, etc. to int, float
        feature_dict[col] = [val]
    return feature_dict


# Example usage:

