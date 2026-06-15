import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score

class ModelManager:
    def __init__(self, models=None, metrics=None):
        self._models = models if models is not None else {}
        self._metrics = metrics if metrics is not None else {}

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