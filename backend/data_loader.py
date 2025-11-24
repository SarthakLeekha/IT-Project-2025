import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler

def _data_dir():
    """Get the correct data directory path"""
    possible_paths = [
        'data',                     
        '../data',                 
        '.',                       
        '../backend/data',         
        'backend/data'             
    ]

    for path in possible_paths:
        if os.path.exists(path):
            files = os.listdir(path)
            data_files = ['crop_data.csv', 'analysis.xlsx', 'ferilizer recommendation.xlsx']
            if any(file in files for file in data_files):
                print(f" Found data directory: {os.path.abspath(path)}")
                return os.path.abspath(path)

    print("Could not find data directory")
    return os.path.abspath('.')

def _read_file(file_path):
    """Read file with multiple format support"""
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            try:
                return pd.read_csv(file_path)
            except:
                return pd.read_excel(file_path)
    except Exception as e:
        print(f" Error reading {file_path}: {e}")
        return None

def load_real_crop_data():
    """Load and preprocess crop recommendation data"""
    d = _data_dir()
    print(f" Looking for crop data in: {d}")

    possible_files = [
        'crop_data.csv',
        'crop recommendation csv.xlsx', 
        'crop recommendation csv.csv',
        'crop_data.xlsx'
    ]

    df = None
    for file in possible_files:
        file_path = os.path.join(d, file)
        print(f" Checking: {file_path}")
        if os.path.exists(file_path):
            df = _read_file(file_path)
            if df is not None:
                print(f" Loaded crop data from: {file}")
                break

    if df is None:
        print(" Could not load crop data from any known file")
        print(" Creating sample crop data for testing...")
        return create_sample_crop_data()

    df.columns = [col.strip().lower() for col in df.columns]
    print(f" Crop dataset columns: {list(df.columns)}")

    column_mapping = {
        'n': 'N', 'p': 'P', 'k': 'K',
        'temperature': 'temperature', 'temp': 'temperature',
        'humidity': 'humidity', 'humid': 'humidity',
        'ph': 'ph', 'pH': 'ph',
        'rainfall': 'rainfall', 'rain': 'rainfall',
        'label': 'label', 'crop': 'label'
    }

    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

    required_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print(f" Missing columns in crop data: {missing_columns}")
        print(" Creating sample crop data...")
        return create_sample_crop_data()

    print(f" Crop dataset: {len(df)} samples, {df['label'].nunique()} crops")
    print(f" Crops available: {', '.join(df['label'].unique()[:5])}...")

    return df

def load_real_soil_data():
    """Load and preprocess soil analysis data"""
    d = _data_dir()
    print(f"Looking for soil data in: {d}")

    possible_files = [
        'analysis.xlsx',
        'analysis.csv',
        'soil_data.csv'
    ]

    df = None
    for file in possible_files:
        file_path = os.path.join(d, file)
        print(f" Checking: {file_path}")
        if os.path.exists(file_path):
            df = _read_file(file_path)
            if df is not None:
                print(f" Loaded soil data from: {file}")
                break

    if df is None:
        print("Could not load soil data from any known file")
        print(" Creating sample soil data for testing...")
        return create_sample_soil_data()

    df.columns = [col.strip().lower() for col in df.columns]
    print(f"Soil dataset columns: {list(df.columns)}")

    nutrient_cols = []
    for col in df.columns:
        if 'nitrogen' in col or 'n' == col:
            nutrient_cols.append(col)
            df = df.rename(columns={col: 'nitrogen'})
        elif 'phosphorus' in col or 'phosphorous' in col or 'p' == col:
            nutrient_cols.append(col)
            df = df.rename(columns={col: 'phosphorus'})
        elif 'potassium' in col or 'k' == col:
            nutrient_cols.append(col)
            df = df.rename(columns={col: 'potassium'})
        elif 'ph' in col:
            df = df.rename(columns={col: 'ph'})
        elif 'organic' in col or 'carbon' in col:
            df = df.rename(columns={col: 'organic_carbon'})
        elif 'moisture' in col:
            df = df.rename(columns={col: 'moisture'})
            
            moisture_mapping = {'low': 1, 'medium': 2, 'high': 3}
            if df['moisture'].dtype == 'object':
                df['moisture'] = df['moisture'].map(moisture_mapping).fillna(2).astype(int)

    if 'fertility' not in df.columns:
        if all(nut in df.columns for nut in ['nitrogen', 'phosphorus', 'potassium']):
            
            nutrient_mapping = {'low': 1, 'medium': 2, 'high': 3}
            for col in ['nitrogen', 'phosphorus', 'potassium']:
                if col in df.columns:
                    df[col] = df[col].map(nutrient_mapping).fillna(0).astype(int)
            total_nutrients = df['nitrogen'] + df['phosphorus'] + df['potassium']
            df['fertility'] = pd.qcut(total_nutrients, q=3, labels=['Low', 'Medium', 'High'])
        else:
            df['fertility'] = np.random.choice(['Low', 'Medium', 'High'], len(df))

    print(f" Soil dataset: {len(df)} samples")
    return df

def load_real_fertilizer_data():
    """Load and preprocess fertilizer recommendation data"""
    d = _data_dir()
    print(f" Looking for fertilizer data in: {d}")

    possible_files = [
        'soil_data.xlsx',
        'ferilizer recommendation.xlsx',
        'fertilizer recommendation.xlsx',
        'fertilizer_data.csv',
        'fertilizer_data.xlsx'
    ]

    df = None
    for file in possible_files:
        file_path = os.path.join(d, file)
        print(f" Checking: {file_path}")
        if os.path.exists(file_path):
            df = _read_file(file_path)
            if df is not None:
                print(f" Loaded fertilizer data from: {file}")
                break

    if df is None:
        print(" Could not load fertilizer data from any known file")
        print(" Creating sample fertilizer data for testing...")
        return create_sample_fertilizer_data()

    
    df.columns = [col.strip().lower() for col in df.columns]
    print(f"Fertilizer dataset columns: {list(df.columns)}")

    
    column_mapping = {
        'crop type': 'crop_type', 'crop': 'crop_type', 'croptype': 'crop_type',
        'soil type': 'soil_type', 'soil': 'soil_type', 'soiltype': 'soil_type',
        'fertilizer name': 'fertilizer', 'fertilizer': 'fertilizer', 'fertilizer_type': 'fertilizer',
        'n': 'nitrogen', 'nitrogen': 'nitrogen', 'nitrogen_level': 'nitrogen',
        'p': 'phosphorus', 'phosphorous': 'phosphorus', 'phosphorus': 'phosphorus', 'phosphorus_level': 'phosphorus',
        'k': 'potassium', 'potassium': 'potassium', 'potassiumm': 'potassium', 'potassium_level': 'potassium',
        'temparature': 'temperature', 'temperature': 'temperature',
        'humidity ': 'humidity', 'humidity': 'humidity',
        'moisture': 'moisture',
        'nitrogen_deficiency': 'nitrogen_deficiency',
        'phosphorus_deficiency': 'phosphorus_deficiency',
        'potassium_deficiency': 'potassium_deficiency'
    }

    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})

    
    required_cols = ['crop_type', 'soil_type', 'nitrogen', 'phosphorus', 'potassium', 'fertilizer']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f" Missing required columns: {missing_cols}")
        print("Creating sample fertilizer data...")
        return create_sample_fertilizer_data()

    
    if 'crop_type' in df.columns and 'soil_type' in df.columns:
        for nutrient in ['nitrogen', 'phosphorus', 'potassium']:
            if nutrient in df.columns:
                deficiency_col = f'{nutrient}_deficiency'
                if deficiency_col not in df.columns:
                    threshold = df[nutrient].median()
                    df[deficiency_col] = (df[nutrient] < threshold).astype(int)

    print(f" Fertilizer dataset: {len(df)} samples")
    print(f" Available crops: {df['crop_type'].unique()[:5] if 'crop_type' in df.columns else 'N/A'}")
    print(f" Available fertilizers: {df['fertilizer'].unique()[:5] if 'fertilizer' in df.columns else 'N/A'}")
    return df

def create_sample_crop_data():
    """Create sample crop data for testing"""
    np.random.seed(42)
    n_samples = 100

    data = {
        'N': np.random.uniform(0, 140, n_samples),
        'P': np.random.uniform(5, 145, n_samples),
        'K': np.random.uniform(5, 205, n_samples),
        'temperature': np.random.uniform(8, 44, n_samples),
        'humidity': np.random.uniform(14, 100, n_samples),
        'ph': np.random.uniform(3.5, 10, n_samples),
        'rainfall': np.random.uniform(20, 300, n_samples),
        'label': np.random.choice(['rice', 'wheat', 'maize', 'cotton', 'sugarcane'], n_samples)
    }

    df = pd.DataFrame(data)
    print(" Created sample crop data")
    return df

def create_sample_soil_data():
    """Create sample soil data for testing"""
    np.random.seed(42)
    n_samples = 100

    data = {
        'ph': np.random.uniform(4.0, 9.0, n_samples),
        'organic_carbon': np.random.uniform(0.1, 5.0, n_samples),
        'nitrogen': np.random.uniform(50, 500, n_samples),
        'phosphorus': np.random.uniform(5, 100, n_samples),
        'potassium': np.random.uniform(50, 500, n_samples),
        'fertility': np.random.choice(['Low', 'Medium', 'High'], n_samples)
    }

    df = pd.DataFrame(data)
    print(" Created sample soil data")
    return df

def create_sample_fertilizer_data():
    """Create sample fertilizer data for testing"""
    np.random.seed(42)
    n_samples = 100

    data = {
        'crop_type': np.random.choice(['wheat', 'rice', 'maize', 'cotton'], n_samples),
        'soil_type': np.random.choice(['Clay', 'Sandy', 'Loamy'], n_samples),
        'N_deficiency': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
        'P_deficiency': np.random.choice([0, 1], n_samples, p=[0.5, 0.5]),
        'K_deficiency': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
        'fertilizer': np.random.choice(['Urea', 'DAP', 'MOP', 'NPK'], n_samples)
    }

    df = pd.DataFrame(data)
    print("Created sample fertilizer data")
    return df

def get_crop_details(crop_name):
    """Return detailed crop information"""
    crop_info = {
        'rice': {
            'season': 'Kharif/Rabi', 
            'water_requirements': 'High',
            'soil_type': 'Clay loam', 
            'duration': '90-150 days',
            'temperature': '20-35C',
            'rainfall': '150-300 cm'
        },
        'wheat': {
            'season': 'Rabi', 
            'water_requirements': 'Medium',
            'soil_type': 'Well-drained loamy', 
            'duration': '110-130 days',
            'temperature': '10-25C',
            'rainfall': '50-100 cm'
        },
        'maize': {
            'season': 'Kharif', 
            'water_requirements': 'Medium',
            'soil_type': 'Well-drained soil', 
            'duration': '80-100 days',
            'temperature': '18-27C',
            'rainfall': '60-120 cm'
        },
        'cotton': {
            'season': 'Kharif', 
            'water_requirements': 'Medium to High',
            'soil_type': 'Black soil', 
            'duration': '150-180 days',
            'temperature': '21-30C',
            'rainfall': '50-100 cm'
        },
        'sugarcane': {
            'season': 'Throughout year', 
            'water_requirements': 'High',
            'soil_type': 'Deep rich loamy', 
            'duration': '12-18 months',
            'temperature': '20-30C',
            'rainfall': '150-200 cm'
        }
    }

    return crop_info.get(crop_name.lower(), {
        'season': 'Varies', 
        'water_requirements': 'Moderate',
        'soil_type': 'Well-drained', 
        'duration': '90-120 days',
        'temperature': '15-30C',
        'rainfall': '50-150 cm'
    })