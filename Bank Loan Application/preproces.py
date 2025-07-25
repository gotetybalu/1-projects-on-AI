import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

def prepare_features(df, target_column='Loan Approved status'):
    # Drop ID and reason columns from features
    X = df.drop(columns=['Candidate ID', target_column, 'Reason for approval or rejected'])
    y = df[target_column]

    # Encode target variable
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    categorical_features = ['Regime']  # categorical column to one-hot encode
    numerical_features = X.select_dtypes(include=np.number).columns.tolist()
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='passthrough'  # passthrough if other columns present
    )

    feature_columns = X.columns.tolist()

    return X, y_encoded, preprocessor, le, numerical_features, categorical_features, feature_columns
