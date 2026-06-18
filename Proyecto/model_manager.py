import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import io
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

class ModelManager:

    @staticmethod
    def extract_dataframe_from_notebook(notebook_path):
        """
        Reads a Jupyter Notebook (.ipynb) file and extracts structured dataframe data
        from its execution cell outputs into a pandas DataFrame.
        """
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb_data = json.load(f)
            
            for cell in nb_data.get('cells', []):
                if cell.get('cell_type') == 'code':
                    for output in cell.get('outputs', []):
                        if 'data' in output and 'text/csv' in output['data']:
                            csv_data = output['data']['text/csv']
                            return pd.read_csv(io.StringIO(''.join(csv_data)))
                        if 'data' in output and 'application/json' in output['data']:
                            json_data = output['data']['application/json']
                            return pd.DataFrame(json_data)
            print("[INFO] No direct unmarshalled data found in notebook execution units.")
            return None
        except Exception as e:
            print(f"[CRITICAL] Error parsing Jupyter Notebook structural cells: {e}")
            return None

    @staticmethod
    def run_kmeans_clustering(df):
        print("\n--- Starting Adaptive K-Means Clustering Pipeline ---")
        plt.ioff() # Mantener apagado el modo interactivo global

        # 1. DYNAMIC PREPROCESSING & TYPE PROTECTION
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

        if not num_cols and not cat_cols:
            print("[ERROR] The active dataset does not contain valid features for analysis.")
            return None

        print(f"[INFO] Numerical features detected: {num_cols}")
        print(f"[INFO] Categorical features detected: {cat_cols}")

        if cat_cols:
            print("[INFO] Transforming categorical variables via One-Hot Encoding...")
            df_processed = pd.get_dummies(df, columns=cat_cols, drop_first=False)
        else:
            df_processed = df[num_cols].copy()

        df_processed = df_processed.astype('float32').dropna()
        X_values = df_processed.values

        if X_values.shape[0] < 3:
            print("[ERROR] Insufficient matrix records to evaluate structural clusters.")
            return None

        # 2. FEATURE SCALING
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_values)

        # 3. ADAPTIVE PCA DIMENSIONALITY REDUCTION
        if X_scaled.shape[1] > 2:
            pca = PCA(n_components=0.90, random_state=42)
            X_pca = pca.fit_transform(X_scaled)
            print(f"[INFO] Dimensions reduced via PCA from {X_scaled.shape[1]} to {X_pca.shape[1]} (90% Variance).")
        else:
            X_pca = X_scaled
            print("[INFO] Dataset dimensions <= 2. Adaptive PCA bypassed.")

        # Strict 2D Projection for Spatial Scatter Partition Visualization
        if X_scaled.shape[1] >= 2:
            pca_2d = PCA(n_components=2, random_state=42)
            X_2d = pca_2d.fit_transform(X_scaled)
        else:
            X_2d = np.column_stack((X_scaled[:, 0], np.zeros(X_scaled.shape[0])))

        # 4. MULTI-K HYPERPARAMETER METRICS EVALUATION
        max_k = min(15, X_values.shape[0] - 1)
        k_values = [k for k in [2, 3, 4, 5, 6, 8, 10, 12] if k <= max_k]

        if len(k_values) < 2:
            k_values = [2]

        results = []
        models = {}
        labels_by_k = {}

        for k in k_values:
            kmeans = KMeans(n_clusters=k, init='k-means++', n_init=10, max_iter=300, random_state=42)
            labels = kmeans.fit_predict(X_pca)

            inertia = kmeans.inertia_
            sample_size_sil = min(3000, X_pca.shape[0])
            
            silhouette = silhouette_score(X_pca, labels, sample_size=sample_size_sil, random_state=42)
            calinski = calinski_harabasz_score(X_pca, labels)
            davies = davies_bouldin_score(X_pca, labels)

            results.append({
                'k': k,
                'inercia_intra_cluster': inertia,
                'silhouette_intra_inter': silhouette,
                'calinski_harabasz_inter_intra': calinski,
                'davies_bouldin_intra_inter': davies
            })
            models[k] = kmeans
            labels_by_k[k] = labels

        results_df = pd.DataFrame(results)

        # 5. AUTOMATED RANKING CRITERIA SYSTEM FOR BEST K
        ranking_df = results_df.copy()
        ranking_df['rank_silhouette'] = ranking_df['silhouette_intra_inter'].rank(ascending=False)
        ranking_df['rank_calinski'] = ranking_df['calinski_harabasz_inter_intra'].rank(ascending=False)
        ranking_df['rank_davies'] = ranking_df['davies_bouldin_intra_inter'].rank(ascending=True)
        ranking_df['rank_promedio'] = ranking_df[['rank_silhouette', 'rank_calinski', 'rank_davies']].mean(axis=1)

        ranking_df = ranking_df.sort_values('rank_promedio')
        best_k = int(ranking_df.iloc[0]['k'])
        best_labels = labels_by_k[best_k]
        best_model = models[best_k]

        print(f"\n[SYSTEM] Optimal Model Selection: K={best_k} suggested based on structural ranking metrics.")
        print(ranking_df[['k', 'silhouette_intra_inter', 'calinski_harabasz_inter_intra', 'davies_bouldin_intra_inter', 'rank_promedio']].to_string(index=False))

        # 6. LOG DISTRIBUTION DATA TO WORKSPACE FILING
        df_output = df.copy()
        df_output['Cluster_Asignado'] = best_labels

        print("\n========== STRUCTURAL CLUSTER DISTRIBUTION PROFILE ==========")
        cluster_counts = pd.Series(best_labels).value_counts().sort_index()
        for cluster_id, count in cluster_counts.items():
            percentage = (count / len(best_labels)) * 100
            print(f"Cluster {cluster_id}: {count} records ({percentage:.2f}%)")

        df_output.to_csv("resultado_clustering.csv", index=False)
        with open("reporte_clustering.txt", "w", encoding="utf-8") as f:
            f.write("ADVANCED CLUSTERING PIPELINE EXECUTION REPORT\n")
            f.write("=============================================\n\n")
            f.write(f"Target Optimized Selected K Parameter: {best_k}\n\n")
            f.write(ranking_df.to_string())

        print("\n[SUCCESS] Pipeline metrics saved to: resultado_clustering.csv")
        print("[SUCCESS] Comprehensive text report compiled at: reporte_clustering.txt")

        # Retornamos un diccionario con los datos limpios para que main.py construya los plots secuencialmente
        payload = {
            "df_output": df_output,
            "results_df": results_df,
            "X_2d": X_2d,
            "best_labels": best_labels,
            "best_k": best_k,
            "cluster_centers": best_model.cluster_centers_,
            "X_values": X_values
        }
        return payload

    @staticmethod
    def run_knn_imputation(df, target_column, k_values=[3,5,7,9]):
        print("\n--- Starting Adaptive k-NN Imputation Pipeline ---")

        if target_column not in df.columns:
            print(f"[ERROR] Column '{target_column}' not found.")
            return None, None, None

        if df[target_column].isna().sum() == 0:
            print("[INFO] No missing values detected.")
            return df.copy(), None, None

        df_work = df.copy()

        # Separate known and unknown rows
        train_df = df_work[df_work[target_column].notna()].copy()
        predict_df = df_work[df_work[target_column].isna()].copy()

        if len(train_df) < 5:
            print("[ERROR] Not enough known observations.")
            return None, None, None

        # Features
        X_train = train_df.drop(columns=[target_column])
        X_predict = predict_df.drop(columns=[target_column])

        # One-hot encode features
        X_all = pd.concat([X_train, X_predict], axis=0)
        X_all = pd.get_dummies(X_all, drop_first=False)

        X_train = X_all.iloc[:len(X_train)]
        X_predict = X_all.iloc[len(X_train):]

        X_train = X_train.fillna(X_train.median(numeric_only=True))
        X_predict = X_predict.fillna(X_train.median(numeric_only=True))

        # Determine target type
        target_is_numeric = pd.api.types.is_numeric_dtype(train_df[target_column])

        results = []

        if target_is_numeric:
            y_train = train_df[target_column]

            print("[INFO] Numerical target detected.")
            print("[INFO] Using KNeighborsRegressor.")

            best_score = -np.inf
            best_model = None
            best_k = None

            for k in k_values:
                if k >= len(X_train):
                    continue

                model = KNeighborsRegressor(n_neighbors=k)
                scores = cross_val_score(
                    model,
                    X_train,
                    y_train,
                    cv=5,
                    scoring='neg_mean_squared_error'
                )

                mean_score = scores.mean()
                results.append({
                    "k": k,
                    "cv_score": mean_score
                })

                if mean_score > best_score:
                    best_score = mean_score
                    best_model = model
                    best_k = k

        else:
            encoder = LabelEncoder()
            y_train = encoder.fit_transform(
                train_df[target_column].astype(str)
            )

            print("[INFO] Categorical target detected.")
            print("[INFO] Using KNeighborsClassifier.")

            best_score = -np.inf
            best_model = None
            best_k = None

            for k in k_values:
                if k >= len(X_train):
                    continue

                model = KNeighborsClassifier(n_neighbors=k)
                scores = cross_val_score(
                    model,
                    X_train,
                    y_train,
                    cv=5,
                    scoring='accuracy'
                )

                mean_score = scores.mean()
                results.append({
                    "k": k,
                    "cv_score": mean_score
                })

                if mean_score > best_score:
                    best_score = mean_score
                    best_model = model
                    best_k = k

        evaluation_df = pd.DataFrame(results)

        print("\n===== KNN MODEL EVALUATION =====")
        print(evaluation_df.to_string(index=False))

        print(f"\n[SYSTEM] Best k selected: {best_k}")

        # Train final model
        best_model.fit(X_train, y_train)
        predictions = best_model.predict(X_predict)

        if not target_is_numeric:
            predictions = encoder.inverse_transform(
                predictions.astype(int)
            )

        # Fill missing values
        df_work.loc[df_work[target_column].isna(), target_column] = predictions

        print(f"[SUCCESS] {len(predictions)} missing values imputed in column '{target_column}'.")

        return df_work, best_k, evaluation_df