import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import resample
import joblib
import os
import json

def load_and_preprocess_data():
    """Load fertilizer data and preprocess for better model performance"""
    df = pd.read_excel('data/fertilizer_data.xlsx')

    le_crop = LabelEncoder()
    le_soil = LabelEncoder()
    le_fert = LabelEncoder()

    df['crop_encoded'] = le_crop.fit_transform(df['crop_type'])
    df['soil_encoded'] = le_soil.fit_transform(df['soil_type'])
    df['fert_encoded'] = le_fert.fit_transform(df['fertilizer_type'])

    level_map = {'low': 0, 'medium': 1, 'high': 2}
    df['n_encoded'] = df['nitrogen_level'].map(level_map)
    df['p_encoded'] = df['phosphorus_level'].map(level_map)
    df['k_encoded'] = df['potassium_level'].map(level_map)

    df['total_nutrient_score'] = df['n_encoded'] + df['p_encoded'] + df['k_encoded']
    df['npk_ratio'] = df['n_encoded'] / (df['p_encoded'] + df['k_encoded'] + 1)  # Avoid division by zero
    df['deficiency_count'] = df['nitrogen_deficiency'] + df['phosphorus_deficiency'] + df['potassium_deficiency']

    features = [
        'soil_ph', 'n_encoded', 'p_encoded', 'k_encoded',
        'crop_encoded', 'soil_encoded', 'total_nutrient_score',
        'npk_ratio', 'deficiency_count'
    ]

    X = df[features]
    y = df['fert_encoded']

    return X, y, le_crop, le_soil, le_fert, features

def balance_dataset(X, y):
    """Balance the dataset using oversampling"""
    data = pd.concat([X, y], axis=1)
    target_col = y.name

    max_samples = data[target_col].value_counts().max()

    balanced_dfs = []
    for class_label in data[target_col].unique():
        class_df = data[data[target_col] == class_label]
        if len(class_df) < max_samples:
            oversampled = resample(class_df, replace=True, n_samples=max_samples, random_state=42)
            balanced_dfs.append(oversampled)
        else:
            balanced_dfs.append(class_df)

    balanced_data = pd.concat(balanced_dfs)
    X_balanced = balanced_data.drop(target_col, axis=1)
    y_balanced = balanced_data[target_col]

    return X_balanced, y_balanced

def train_improved_model():
    """Train an improved fertilizer recommendation model"""
    print("Loading and preprocessing data...")
    X, y, le_crop, le_soil, le_fert, features = load_and_preprocess_data()

    print(f"Original dataset: {X.shape[0]} samples, {len(np.unique(y))} classes")
    print(f"Original class distribution: {pd.Series(y).value_counts().sort_index().values}")

    print("Balancing dataset...")
    X_balanced, y_balanced = balance_dataset(X, y)
    print(f"Balanced dataset: {X_balanced.shape[0]} samples")
    print(f"Balanced class distribution: {pd.Series(y_balanced).value_counts().sort_index().values}")

    X_train, X_test, y_train, y_test = train_test_split(
        X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Training improved model...")
    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )

    cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5)
    print(f"Cross-validation scores: {cv_scores}")
    print(f"Mean CV score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

    rf_model.fit(X_train_scaled, y_train)

    y_pred = rf_model.predict(X_test_scaled)
    print("\nTest Set Performance:")
    print(classification_report(y_test, y_pred, target_names=le_fert.classes_))

    feature_importance = dict(zip(features, rf_model.feature_importances_))
    print("\nFeature Importance:")
    for feat, imp in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True):
        print(f"{feat}: {imp:.4f}")

    os.makedirs('backend/models', exist_ok=True)

    joblib.dump(rf_model, 'backend/models/fertilizer_model_improved.pkl')
    joblib.dump(scaler, 'backend/models/fertilizer_scaler.pkl')
    joblib.dump(le_crop, 'backend/models/fertilizer_crop_encoder.pkl')
    joblib.dump(le_soil, 'backend/models/fertilizer_soil_encoder.pkl')
    joblib.dump(le_fert, 'backend/models/fertilizer_encoder.pkl')

    metrics = {
        "fertilizer": {
            "accuracy": cv_scores.mean(),
            "cross_validation": f"{cv_scores.mean():.4f}  {cv_scores.std():.4f}",
            "dataset_size": len(X_balanced),
            "num_fertilizers": len(le_fert.classes_),
            "class_distribution": {le_fert.classes_[i]: count for i, count in enumerate(pd.Series(y_balanced).value_counts().sort_index())},
            "improvements": "Balanced dataset, additional features, hyperparameter tuning"
        }
    }

    with open('backend/models/training_metrics_improved.json', 'w') as f:
        json.dump(metrics, f, indent=2)

    print("\nImproved model saved successfully!")
    print("Files saved:")
    print("- backend/models/fertilizer_model_improved.pkl")
    print("- backend/models/fertilizer_scaler.pkl")
    print("- backend/models/fertilizer_crop_encoder.pkl")
    print("- backend/models/fertilizer_soil_encoder.pkl")
    print("- backend/models/fertilizer_encoder.pkl")
    print("- backend/models/training_metrics_improved.json")

    return rf_model, scaler, le_crop, le_soil, le_fert

if __name__ == "__main__":
    train_improved_model()
