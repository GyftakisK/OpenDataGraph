import joblib
import numpy as np
import os
from node_ranker.ranksvm import RankSVM


class MLRanker:
    def __init__(self):
        self.__model = None
        self.__pagerank_scaler = None
        self.__node2vec_scaler = None
        self.__selected_sem_types = None

    def load_model(self, model_name):
        script_path = os.path.dirname(os.path.realpath(__file__))
        if model_name == "RankSVM":
            self.__model = RankSVM(C=0.01, random_state=2020)
            self.__model.coefs = joblib.load(os.path.join(script_path, "rankSVMcoefs.joblib"))
            self.__model._fitted = True
        self.__pagerank_scaler = joblib.load(os.path.join(script_path, "pagerank_scaler.joblib"))
        self.__node2vec_scaler = joblib.load(os.path.join(script_path, "node2vec32_scaler.joblib"))
        self.__selected_sem_types = joblib.load(os.path.join(script_path, "selected_sem_types.joblib"))

    def rank_nodes(self, feature_data: dict):
        x = self._get_feature_array_from_data(feature_data)
        ranking = self.__model.predict(x)
        return dict(zip(list(feature_data.keys()), ranking.tolist()))

    def _get_feature_array_from_data(self, feature_data):
        X_test_node2vec32 = self.__node2vec_scaler.transform(np.asarray([data["node2vec32"]
                                                                         for data in feature_data.values()]))
        X_test_selected_sem = self._one_hot_encode_sem_types(feature_data)
        X_test_pagerank = self.__pagerank_scaler.transform(np.asarray([[data["pagerank"]]
                                                                       for data in feature_data.values()]))
        return np.concatenate([X_test_node2vec32, X_test_selected_sem, X_test_pagerank], axis=1)

    def _one_hot_encode_sem_types(self, feature_data):
        selected_test_sem_types_one_hot = []
        for data in feature_data.values():
            row = [1 if sem_type in data["sem_types"] else 0 for sem_type in self.__selected_sem_types]
            selected_test_sem_types_one_hot.append(row)
        return np.asarray(selected_test_sem_types_one_hot)
