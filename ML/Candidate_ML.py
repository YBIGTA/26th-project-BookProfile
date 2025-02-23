#!/usr/bin/env python
"""
Module: clustering_module.py
Description:
    - MongoDB에서 데이터를 불러와 DataFrame으로 변환
    - 텍스트 임베딩 생성 및 평균 임베딩 계산
    - t-SNE와 UMAP을 활용한 차원 축소 및 K-Means 클러스터링 (그리드 서치 포함)
    - 각 클러스터별 대표 book_id 도출 및 Plotly 시각화 제공
    - 결과(시각화 HTML, centroid JSON, 하이퍼파라미터 CSV)를 실행 시각별 폴더에 저장

"""

import os
import math
import json
import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import umap
import plotly.express as px
from datetime import datetime
from sentence_transformers import SentenceTransformer
import warnings

# 1) n_jobs 관련 UserWarning 제거
warnings.filterwarnings(
    "ignore", 
    message="n_jobs value 1 overridden to 1 by setting random_state"
)

# 2) FutureWarning 중 'force_all_finite' 메시지 제거
warnings.filterwarnings(
    "ignore", 
    message="'force_all_finite' was renamed to 'ensure_all_finite' in 1.6"
)

# ============================================================
# 1. DB 연결 및 데이터 불러오기
# ============================================================
class MongoDBHandler:
    """
    MongoDB 연결 및 데이터 조회를 위한 클래스.
    """
    def __init__(self, uri, db_name):
        """
        :param uri: MongoDB 연결 URI
        :param db_name: 사용할 데이터베이스 이름
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection_df(self, collection_name, query={}):
        """
        지정한 컬렉션에서 데이터를 조회하여 DataFrame으로 반환.
        
        :param collection_name: 컬렉션 이름
        :param query: MongoDB 쿼리 (기본값은 전체 조회)
        :return: DataFrame 형태의 데이터
        """
        collection = self.db[collection_name]
        cursor = collection.find(query)
        return pd.DataFrame(list(cursor))


# ============================================================
# 2. 임베딩 처리
# ============================================================
class Embedder:
    """
    주어진 모델을 활용하여 텍스트 임베딩을 생성하는 클래스.
    """
    def __init__(self, model):
        """
        :param model: 텍스트 임베딩 모델 (예: SentenceTransformer)
        """
        self.model = model

    def get_embedding(self, text):
        """
        텍스트 임베딩을 반환. 빈 문자열이나 None인 경우 빈 문자열로 처리.
        
        :param text: 임베딩을 생성할 텍스트
        :return: 임베딩 벡터 (numpy array)
        """
        if not text:
            text = ""
        return self.model.encode(text)

    def add_embedding_column(self, df, text_column, new_column='embedding'):
        """
        DataFrame의 지정한 텍스트 칼럼에 대해 임베딩 컬럼을 추가.
        
        :param df: 원본 DataFrame
        :param text_column: 임베딩 대상 텍스트 칼럼 이름
        :param new_column: 생성할 임베딩 칼럼 이름
        :return: 임베딩 컬럼이 추가된 DataFrame
        """
        df[new_column] = df[text_column].apply(self.get_embedding)
        return df


def mean_embedding(embeddings):
    """
    여러 임베딩 벡터의 평균을 계산.
    
    :param embeddings: numpy array 형태의 임베딩 리스트 또는 Series
    :return: 평균 임베딩 벡터 또는 None
    """
    emb_list = list(embeddings)
    if len(emb_list) == 0:
        return None
    return np.mean(emb_list, axis=0)


def aggregate_embeddings(df, group_by_field, embedding_column):
    """
    동일 그룹(예: book_id) 내 임베딩 벡터들의 평균값과 리뷰 개수를 계산.
    
    :param df: 원본 DataFrame
    :param group_by_field: 그룹화 기준 컬럼 (예: 'book_id')
    :param embedding_column: 임베딩이 저장된 컬럼 (예: 'review_embedding')
    :return: 그룹별 평균 임베딩 및 리뷰 개수를 포함하는 DataFrame
    """
    grouped = df.groupby(group_by_field)
    agg_df = grouped.agg(
        number_of_reviews=(embedding_column, 'count'),
        embedding_mean=(embedding_column, mean_embedding)
    ).reset_index()
    agg_df[group_by_field] = agg_df[group_by_field].astype(str)
    return agg_df


# ============================================================
# 3. t-SNE 기반 클러스터링 및 시각화
# ============================================================
class TSNEClustering:
    """
    t-SNE 차원 축소, K-Means 클러스터링 및 하이퍼파라미터 그리드 서치를 수행하는 클래스.
    """
    def __init__(self, embedding_matrix):
        """
        :param embedding_matrix: 임베딩 행렬 (numpy array)
        """
        self.embedding_matrix = embedding_matrix
        self.tsne_results = {}  # t-SNE 결과 DataFrame 저장
        self.results = []       # 그리드 서치 결과 저장

    def grid_search(self, dimensions=range(2, 4), perplexities=np.arange(0.5, 10.5, 0.25), k_values=range(5, 11)):
        """
        t-SNE 및 K-Means 하이퍼파라미터 그리드 서치 수행.
        
        :param dimensions: t-SNE 차원 후보 (예: 2~3)
        :param perplexities: t-SNE perplexity 후보
        :param k_values: K-Means 군집 수 후보
        """
        print("Starting t-SNE grid search...")
        for dim in dimensions:
            for perp in perplexities:
                tsne = TSNE(n_components=dim, perplexity=perp, random_state=42)
                X_tsne = tsne.fit_transform(self.embedding_matrix)
                key = f"tsne_{dim}_{perp:.2f}"
                df_tsne = pd.DataFrame(X_tsne, columns=[f"tsne_{i}" for i in range(dim)])
                self.tsne_results[key] = df_tsne

                for k in k_values:
                    kmeans = KMeans(n_clusters=k, random_state=42)
                    labels = kmeans.fit_predict(X_tsne)
                    sil_score = silhouette_score(X_tsne, labels)
                    self.results.append({
                        "tsne_dimension": dim,
                        "perplexity": round(perp, 2),
                        "k": k,
                        "silhouette_score": sil_score,
                        "tsne_key": key
                    })
        print("t-SNE grid search completed.")

    def get_results_df(self):
        """
        grid search 결과를 DataFrame으로 반환.
        """
        return pd.DataFrame(self.results)

    def apply_clustering(self, params_row, df_book_embeddings, book_id_col='book_id'):
        """
        주어진 파라미터로 clustering 적용 및 각 클러스터 대표 book_id 도출.
        
        :param params_row: 하이퍼파라미터 정보가 담긴 Series 또는 dict
        :param df_book_embeddings: 그룹별 임베딩 DataFrame (book_id 포함)
        :param book_id_col: book_id 칼럼 이름
        :return: clustering 결과 DataFrame, centroid dictionary
        """
        print(f"Applying t-SNE clustering for params: {params_row.to_dict()}")
        tsne_key = params_row['tsne_key']
        dim = int(params_row['tsne_dimension'])
        k = int(params_row['k'])
        df_tsne = self.tsne_results[tsne_key].copy()
        df_tsne[book_id_col] = df_book_embeddings[book_id_col].values

        feature_cols = [f"tsne_{i}" for i in range(dim)]
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(df_tsne[feature_cols].values)
        df_tsne['cluster'] = labels

        rep_book_ids = {}
        for cluster, group in df_tsne.groupby('cluster'):
            centroid = group[feature_cols].mean().values
            distances = np.linalg.norm(group[feature_cols].values - centroid, axis=1)
            idx = np.argmin(distances)
            rep_book_ids[cluster] = group.iloc[idx][book_id_col]
        print("t-SNE clustering applied.")
        return df_tsne, rep_book_ids

    def visualize(self, df_clustered, tsne_key, params_row):
        """
        Plotly를 이용해 t-SNE clustering 결과 시각화.
        
        :param df_clustered: clustering 결과 DataFrame
        :param tsne_key: 사용한 t-SNE 결과 키
        :param params_row: 하이퍼파라미터 정보
        :return: Plotly figure 객체
        """
        print("Visualizing t-SNE clustering result...")
        dim = int(params_row['tsne_dimension'])
        k = int(params_row['k'])
        sil_score = params_row['silhouette_score']
        fig = None
        if dim == 2:
            fig = px.scatter(
                df_clustered,
                x='tsne_0',
                y='tsne_1',
                color='cluster',
                hover_data=['book_id'],
                title=f"t-SNE 2D ({tsne_key}) k={k}, score={sil_score:.3f}"
            )
            fig.update_layout(
                autosize=False,
                width=700,
                height=700,
                xaxis=dict(scaleanchor="y", scaleratio=1),
                yaxis=dict(scaleanchor="x", scaleratio=1)
            )
        elif dim == 3:
            fig = px.scatter_3d(
                df_clustered,
                x='tsne_0',
                y='tsne_1',
                z='tsne_2',
                color='cluster',
                hover_data=['book_id'],
                title=f"t-SNE 3D ({tsne_key}) k={k}, score={sil_score:.3f}"
            )
            fig.update_layout(
                scene=dict(aspectmode='cube'),
                width=700,
                height=700
            )
        else:
            print("Visualization not supported for dimensions other than 2 or 3.")
        print("t-SNE visualization completed.")
        return fig


# ============================================================
# 4. UMAP 기반 클러스터링 및 시각화
# ============================================================
class UMAPClustering:
    """
    UMAP 차원 축소, K-Means 클러스터링 및 하이퍼파라미터 그리드 서치를 수행하는 클래스.
    """
    def __init__(self, embedding_matrix):
        """
        :param embedding_matrix: 임베딩 행렬 (numpy array)
        """
        self.embedding_matrix = embedding_matrix
        self.umap_results = {}  # UMAP 결과 DataFrame 저장
        self.results = []       # 그리드 서치 결과 저장

    def grid_search(self, n_components_list=range(2, 11), n_neighbors_list=range(2, 11),
                    min_dist_list=np.arange(0.02, 0.151, 0.01), k_values=range(5, 11)):
        """
        UMAP 및 K-Means 하이퍼파라미터 그리드 서치 수행.
        
        :param n_components_list: UMAP 차원 후보
        :param n_neighbors_list: UMAP 이웃 수 후보
        :param min_dist_list: UMAP 최소 거리 후보
        :param k_values: K-Means 군집 수 후보
        """
        print("Starting UMAP grid search...")
        for n_comp in n_components_list:
            for n_neighbors in n_neighbors_list:
                for min_d in min_dist_list:
                    rounded_min_d = round(min_d, 2)  # 근사화된 값 사용
                    reducer = umap.UMAP(
                        n_components=n_comp,
                        n_neighbors=n_neighbors,
                        min_dist=min_d,  # 내부 처리에서는 원래 값 사용
                        random_state=42
                    )
                    X_umap = reducer.fit_transform(self.embedding_matrix)
                    key = f"umap_{n_comp}_{n_neighbors}_{rounded_min_d}"
                    df_umap = pd.DataFrame(X_umap, columns=[f"umap_{i}" for i in range(n_comp)])
                    self.umap_results[key] = df_umap

                    for k in k_values:
                        kmeans = KMeans(n_clusters=k, random_state=42)
                        labels = kmeans.fit_predict(X_umap)
                        sil_score = silhouette_score(X_umap, labels)
                        self.results.append({
                            "umap_n_components": n_comp,
                            "umap_n_neighbors": n_neighbors,
                            "umap_min_dist": rounded_min_d,
                            "k": k,
                            "silhouette_score": sil_score,
                            "umap_key": key
                        })
        print("UMAP grid search completed.")

    def get_results_df(self):
        """
        grid search 결과를 DataFrame으로 반환.
        """
        return pd.DataFrame(self.results)

    def apply_clustering(self, params_row, df_book_embeddings, book_id_col='book_id'):
        """
        주어진 파라미터로 clustering 적용 및 각 클러스터 대표 book_id 도출.
        
        :param params_row: 하이퍼파라미터 정보 Series 또는 dict
        :param df_book_embeddings: 그룹별 임베딩 DataFrame (book_id 포함)
        :param book_id_col: book_id 칼럼 이름
        :return: clustering 결과 DataFrame, centroid dictionary
        """
        print(f"Applying UMAP clustering for params: {params_row.to_dict()}")
        umap_key = params_row['umap_key']
        n_comp = int(params_row['umap_n_components'])
        k = int(params_row['k'])
        df_umap = self.umap_results[umap_key].copy()
        df_umap[book_id_col] = df_book_embeddings[book_id_col].values

        feature_cols = [col for col in df_umap.columns if col.startswith("umap_")]
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(df_umap[feature_cols].values)
        df_umap['cluster'] = labels

        rep_book_ids = {}
        for cluster, group in df_umap.groupby('cluster'):
            centroid = group[feature_cols].mean().values
            distances = np.linalg.norm(group[feature_cols].values - centroid, axis=1)
            idx = np.argmin(distances)
            rep_book_ids[cluster] = group.iloc[idx][book_id_col]
        print("UMAP clustering applied.")
        return df_umap, rep_book_ids

    def visualize(self, df_clustered, umap_key, params_row):
        """
        Plotly를 이용해 UMAP clustering 결과 시각화.
        
        :param df_clustered: clustering 결과 DataFrame
        :param umap_key: 사용한 UMAP 결과 키
        :param params_row: 하이퍼파라미터 정보
        :return: Plotly figure 객체
        """
        print("Visualizing UMAP clustering result...")
        n_comp = int(params_row['umap_n_components'])
        k = int(params_row['k'])
        sil_score = params_row['silhouette_score']
        fig = None
        if n_comp == 2:
            fig = px.scatter(
                df_clustered,
                x='umap_0',
                y='umap_1',
                color='cluster',
                hover_data=['book_id'],
                title=f"UMAP 2D ({umap_key}) k={k}, score={sil_score:.3f}"
            )
            fig.update_layout(
                autosize=False,
                width=700,
                height=700,
                xaxis=dict(scaleanchor="y", scaleratio=1),
                yaxis=dict(scaleanchor="x", scaleratio=1)
            )
        elif n_comp == 3:
            fig = px.scatter_3d(
                df_clustered,
                x='umap_0',
                y='umap_1',
                z='umap_2',
                color='cluster',
                hover_data=['book_id'],
                title=f"UMAP 3D ({umap_key}) k={k}, score={sil_score:.3f}"
            )
            fig.update_layout(
                scene=dict(aspectmode='cube'),
                width=700,
                height=700
            )
        else:
            print("Visualization not supported for dimensions other than 2 or 3.")
        print("UMAP visualization completed.")
        return fig


# ============================================================
# 5. 결과 저장 기능 (시각화 및 centroid 결과)
# ============================================================
class ResultSaver:
    """
    지정한 폴더에 Plotly 시각화(HTML)와 centroid 결과(JSON)를 저장하는 클래스.
    """
    def __init__(self, base_folder):
        """
        :param base_folder: 저장할 최상위 폴더 경로
        """
        self.base_folder = base_folder
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
            print(f"Created directory: {base_folder}")

    def save_figure(self, fig, folder, filename):
        """
        Plotly figure를 HTML 파일로 저장.
        
        :param fig: Plotly figure 객체 (None이면 저장 건너뜀)
        :param folder: 저장할 폴더 경로
        :param filename: 저장할 파일 이름
        """
        if fig is None:
            print("No figure provided to save.")
            return
        if not os.path.exists(folder):
            os.makedirs(folder)
        filepath = os.path.join(folder, filename)
        try:
            fig.write_html(filepath)
            print(f"Figure saved to {filepath}")
        except Exception as e:
            print(f"Failed to save figure: {e}")

    def save_centroids(self, centroids, folder, filename):
        """
        centroid 결과를 JSON 파일로 저장.
        
        :param centroids: dictionary 형태의 centroid 결과
        :param folder: 저장할 폴더 경로
        :param filename: 저장할 파일 이름
        """
        if not os.path.exists(folder):
            os.makedirs(folder)
        filepath = os.path.join(folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(centroids, f, ensure_ascii=False, indent=4)
        print(f"Centroids saved to {filepath}")


# ============================================================
# 6. Main 실행 예제
# ============================================================

def main():
    print("=== Starting clustering pipeline ===")
    
    # 생성할 결과 폴더: result/{YYYYMMDD_HHMMSS}/ with tsne, umap 서브폴더 및 CSV 저장
    base_result = "result"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_folder = os.path.join(base_result, timestamp)
    tsne_result_folder = os.path.join(result_folder, "tsne")
    umap_result_folder = os.path.join(result_folder, "umap")
    for folder in [result_folder, tsne_result_folder, umap_result_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created directory: {folder}")
    
    # --- DB 연결 ---
    print("Connecting to MongoDB and fetching reviews...")
    uri = "mongodb://haneul:1234@3.34.178.2:27017/"
    db_name = "crawling"
    collection_name = "reviews"
    
    db_handler = MongoDBHandler(uri, db_name)
    df_reviews = db_handler.get_collection_df(collection_name)
    print("Fetched reviews data with shape:", df_reviews.shape)
    
    # --- 임베딩 처리 ---
    print("Initializing embedding model and processing reviews...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    if model is None:
        print("Embedding model is not initialized. Please replace the model placeholder with actual model.")
        return

    embedder = Embedder(model)
    df_reviews = embedder.add_embedding_column(df_reviews, text_column='review', new_column='review_embedding')
    
    # --- 그룹별 임베딩 평균 계산 ---
    print("Aggregating embeddings by book_id...")
    df_book_embeddings = aggregate_embeddings(df_reviews, group_by_field='book_id', embedding_column='review_embedding')
    
    # --> 책 별 평균 임베딩 JSON 저장 (book_id, embedding_mean)
    print("Saving book embeddings JSON...")
    # numpy array를 리스트로 변환
    df_book_embeddings_copy = df_book_embeddings[['book_id', 'embedding_mean']].copy()
    df_book_embeddings_copy['embedding_mean'] = df_book_embeddings_copy['embedding_mean'].apply(
        lambda x: x.tolist() if hasattr(x, 'tolist') else x
    )
    book_embeddings_path = os.path.join(result_folder, "book_embeddings.json")
    with open(book_embeddings_path, 'w', encoding='utf-8') as f:
        json.dump(df_book_embeddings_copy.to_dict(orient='records'), f, ensure_ascii=False, indent=4)
    print(f"Book embeddings JSON saved to {book_embeddings_path}")
    
    # --- t-SNE 클러스터링 ---
    print("Starting t-SNE clustering process...")
    embedding_matrix = np.stack(df_book_embeddings['embedding_mean'].values)
    tsne_cluster = TSNEClustering(embedding_matrix)
    tsne_cluster.grid_search()  # grid search 수행
    tsne_df_results = tsne_cluster.get_results_df().sort_values(by='silhouette_score', ascending=False)
    # tsne 결과 CSV 저장
    tsne_csv_path = os.path.join(result_folder, "tsne_results.csv")
    tsne_df_results[['tsne_dimension','perplexity','k','silhouette_score']].to_csv(tsne_csv_path, index=False)
    print(f"t-SNE results CSV saved to {tsne_csv_path}")
    
    # 상위 5개 결과에 대해 clustering 및 시각화 후 결과 저장
    result_saver = ResultSaver(base_folder=result_folder)
    tsne_top5 = tsne_df_results.head(5)
    for idx, row in tsne_top5.iterrows():
        df_clustered, rep_book_ids = tsne_cluster.apply_clustering(row, df_book_embeddings)
        fig = tsne_cluster.visualize(df_clustered, row['tsne_key'], row)
        fname_fig = f"tsne_visualization_{row['tsne_key']}_k{row['k']}_score{row['silhouette_score']:.3f}.html"
        fname_json = f"tsne_centroids_{row['tsne_key']}_k{row['k']}_score{row['silhouette_score']:.3f}.json"
        result_saver.save_figure(fig, tsne_result_folder, fname_fig)
        result_saver.save_centroids(rep_book_ids, tsne_result_folder, fname_json)
    
    # --- UMAP 클러스터링 ---
    print("Starting UMAP clustering process...")
    umap_cluster = UMAPClustering(embedding_matrix)
    umap_cluster.grid_search()  # grid search 수행
    umap_df_results = umap_cluster.get_results_df().sort_values(by='silhouette_score', ascending=False)
    # umap 결과 CSV 저장
    umap_csv_path = os.path.join(result_folder, "umap_results.csv")
    umap_df_results[['umap_n_components','umap_n_neighbors','umap_min_dist','k','silhouette_score']].to_csv(umap_csv_path, index=False)
    print(f"UMAP results CSV saved to {umap_csv_path}")
    
    # 상위 5개 결과에 대해 clustering 및 시각화 후 결과 저장
    umap_top5 = umap_df_results.head(5)
    for idx, row in umap_top5.iterrows():
        df_clustered, rep_book_ids = umap_cluster.apply_clustering(row, df_book_embeddings)
        fig = umap_cluster.visualize(df_clustered, row['umap_key'], row)
        fname_fig = f"umap_visualization_{row['umap_key']}_k{row['k']}_score{row['silhouette_score']:.3f}.html"
        fname_json = f"umap_centroids_{row['umap_key']}_k{row['k']}_score{row['silhouette_score']:.3f}.json"
        result_saver.save_figure(fig, umap_result_folder, fname_fig)
        result_saver.save_centroids(rep_book_ids, umap_result_folder, fname_json)
    
    print("=== Clustering pipeline completed successfully. ===")


if __name__ == '__main__':
    main()
