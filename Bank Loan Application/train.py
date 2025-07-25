from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd

def train_model(X, y, preprocessor, random_state=42):
    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    model = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=random_state))
    ])

    model.fit(X_train, y_train)
    return model, X_test, y_test

def evaluate_model(model, X_test, y_test, label_encoder):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    classification_rep = classification_report(y_test, y_pred, target_names=label_encoder.classes_)
    conf_matrix = confusion_matrix(y_test, y_pred)

    print(f"\nModel Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_rep)
    print("\nConfusion Matrix:")
    print(conf_matrix)

    return accuracy, classification_rep, conf_matrix

def get_feature_importances(model, numerical_features, categorical_features):
    try:
        ohe = model.named_steps['preprocessor'].named_transformers_['cat']
        ohe_feature_names = ohe.get_feature_names_out(categorical_features)
        feature_names = numerical_features + list(ohe_feature_names)
        importances = model.named_steps['classifier'].feature_importances_
        importances_series = pd.Series(importances, index=feature_names).sort_values(ascending=False)
        print("\nTop 10 Feature Importances:")
        print(importances_series.head(10))
        return importances_series
    except Exception as e:
        print(f"Could not get feature importances: {e}")
        return None
