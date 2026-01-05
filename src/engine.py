import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder

class NIDSEngine:
    def __init__(self):
        self.model = None
        self.X_test = None
        self.y_test = None
        self.df = None
        self.label_encoder = LabelEncoder()

    def load_data(self, source_type, file_path=None):
        """
        Switchboard for loading data based on user selection.
        """
        if source_type == 'synthetic':
            self.df = self._generate_synthetic()
        elif source_type == 'csv':
            if not file_path:
                raise ValueError("File path required for CSV mode")
            self.df = self._load_csv(file_path)
        
        return len(self.df)

    def _generate_synthetic(self):
        """Generates mathematical simulation data."""
        np.random.seed(1337)
        n_samples = 5000
        data = {
            'Destination Port': np.random.randint(1, 65535, n_samples),
            'Flow Duration': np.random.randint(100, 100000, n_samples),
            'Total Fwd Packets': np.random.randint(1, 100, n_samples),
            'Packet Length Mean': np.random.uniform(10, 1500, n_samples),
            'Active Mean': np.random.uniform(0, 1000, n_samples),
            'Label': np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3]) 
        }
        df = pd.DataFrame(data)
        # Inject patterns
        attacks = df['Label'] == 1
        df.loc[attacks, 'Total Fwd Packets'] += np.random.randint(50, 300, size=attacks.sum())
        df.loc[attacks, 'Flow Duration'] = np.random.randint(1, 500, size=attacks.sum())
        return df

    def _load_csv(self, file_path):
        """
        Loads and cleans a Real CIC-IDS2017 CSV.
        """
        # Read CSV (handling spaces in headers which CIC dataset has)
        df = pd.read_csv(file_path)
        
        # 1. Clean Column Names (Strip spaces)
        df.columns = df.columns.str.strip()
        
        # 2. Select Relevant Features (Map to our Model)
        # Ensure these columns exist in your CSV. CIC-IDS2017 usually has them.
        required_cols = ['Destination Port', 'Flow Duration', 'Total Fwd Packets', 'Packet Length Mean', 'Active Mean', 'Label']
        
        # Check if columns exist
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise ValueError(f"CSV is missing columns: {missing}")
            
        df = df[required_cols]
        df = df.dropna()
        
        # 3. Handle Labels (Real data has 'BENIGN', 'DDoS', etc. -> needs to be 0 or 1)
        # If label is string, encode it.
        if df['Label'].dtype == 'object':
            # Assume 'BENIGN' is 0, everything else is 1
            df['Label'] = df['Label'].apply(lambda x: 0 if 'BENIGN' in str(x).upper() else 1)
            
        return df

    def train(self, split_ratio, trees):
        if self.df is None:
            raise ValueError("No data loaded.")

        X = self.df.drop('Label', axis=1)
        y = self.df['Label']
        
        test_size = (100 - split_ratio) / 100.0
        X_train, self.X_test, y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        self.model = RandomForestClassifier(n_estimators=trees, random_state=42, n_jobs=-1)
        self.model.fit(X_train, y_train)

    def get_metrics(self):
        if not self.model: return None
        preds = self.model.predict(self.X_test)
        return {
            'accuracy': accuracy_score(self.y_test, preds),
            'cm': confusion_matrix(self.y_test, preds),
            'threats': np.sum(preds)
        }

    def predict_single(self, features):
        if not self.model: return -1
        # features: [Duration, Packets, Length, Active]
        # We need to prepend 'Destination Port' (mocking port 80)
        input_vector = np.array([[80, *features]])
        return self.model.predict(input_vector)[0]