import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score

# Necesario para habilitar IterativeImputer
from sklearn.experimental import enable_iterative_imputer  
from sklearn.impute import IterativeImputer


class ModelManager:
    def __init__(self, models=None, metrics=None):
        self._models = models if models is not None else {}
        self._metrics = metrics if metrics is not None else {}

    @staticmethod
    def knn_classification_imputation(df, target_column, k_values):
        """
        Imputes missing categorical values using KNN classification.

        Parameters
        ----------
        df : pandas.DataFrame
        DataFrame containing the data.
        target_column : str
        Column with missing categorical values.
        k_values : list
        List of k values to evaluate.

        Returns
        -------
        imputed_df : pandas.DataFrame
            DataFrame with missing values imputed.
        metrics : dict
            Cross-validation accuracy for each k.
        best_k : int
            Best k according to cross-validation accuracy.
        """

        data = df.copy()

        # Split rows with and without missing target values
        train_rows = data[data[target_column].notna()]
        predict_rows = data[data[target_column].isna()]

        if predict_rows.empty:
            print("No missing values found.")
            return data, {}, None

        # Features
        X_train = train_rows.drop(columns=[target_column])
        X_predict = predict_rows.drop(columns=[target_column])

        # Target
        y_train = train_rows[target_column]

        # Encode target labels
        label_encoder = LabelEncoder()
        y_train_encoded = label_encoder.fit_transform(y_train)

        # Convert categorical predictors to numeric
        X_all = pd.concat([X_train, X_predict])
        X_all = pd.get_dummies(X_all, drop_first=True)

        X_train = X_all.iloc[:len(X_train)]
        X_predict = X_all.iloc[len(X_train):]

        # Fill any remaining missing predictor values
        imputer = SimpleImputer(strategy="most_frequent")
        X_train = imputer.fit_transform(X_train)
        X_predict = imputer.transform(X_predict)

        # Evaluate k values
        metrics = {}
        for k in k_values:
            knn = KNeighborsClassifier(n_neighbors=k)
            scores = cross_val_score(
                knn,
                X_train,
                y_train_encoded,
                cv=5,
                scoring="accuracy"
            )
            metrics[k] = scores.mean()

        # Select best k
        best_k = max(metrics, key=metrics.get)

        # Train final model
        final_model = KNeighborsClassifier(n_neighbors=best_k)
        final_model.fit(X_train, y_train_encoded)

        # Predict missing values
        predictions = final_model.predict(X_predict)
        predicted_labels = label_encoder.inverse_transform(predictions)

        # Fill missing values
        data.loc[data[target_column].isna(), target_column] = predicted_labels

        return data, metrics, best_k

    @staticmethod
    def mice_imputation(df, max_iter=10):
        """
        Imputación de valores faltantes usando MICE (IterativeImputer).
        Muestra un reporte comparativo del "Antes y Después" inmediatamente.
        """
        if df is None or df.empty:
            print("[ERROR] El DataFrame está vacío o no se ha cargado correctamente.")
            return None

        # Conteo de nulos iniciales por columna
        nulls_before = df.isnull().sum()
        total_nulls_before = nulls_before.sum()

        if total_nulls_before == 0:
            print("[INFO] No hay valores faltantes para imputar.")
            return df

        data = df.copy()
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            print("[ERROR] No hay columnas numéricas en el dataset para aplicar MICE.")
            return data

        try:
            print(f"\n[INFO] Ejecutando MICE (IterativeImputer) en: {numeric_cols}")
            
            imputer = IterativeImputer(max_iter=max_iter, random_state=42)
            imputed_array = imputer.fit_transform(data[numeric_cols])
            
            # Reemplazar valores calculados
            data[numeric_cols] = pd.DataFrame(imputed_array, columns=numeric_cols, index=data.index)
            
            # Conteo de nulos final
            nulls_after = data.isnull().sum()

            # --- REPORTE DE PREVISUALIZACIÓN INMEDIATA ---
            print("\n" + "="*50)
            print("         REPORTE DE IMPUTACIÓN MICE (PREVIEW)       ")
            print("="*50)
            print(f"{'Columna':<30} | {'Nulos Antes':<12} | {'Nulos Después':<12}")
            print("-"*60)
            
            for col in numeric_cols:
                print(f"{col:<30} | {nulls_before[col]:<12} | {nulls_after[col]:<12}")
            
            print("-"*60)
            print(f"Total de registros imputados con éxito: {total_nulls_before - nulls_after.sum()}")
            print("="*50 + "\n")

            print("[SUCCESS] MICE imputation completed successfully.")
            return data
            
        except Exception as e:
            print(f"[CRITICAL] Error durante la imputación MICE: {e}")
            return df

    def clusteringkmeans(self):
        pass

    def save_model(self):
        pass

    def train(self):
        pass

    def predict(self):
        pass

    def Metricasdecalidad(self):
        pass