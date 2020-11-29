# Original file https://github.com/rpmcruz/machine-learning/blob/master/svm/python/ranksvm.py



from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.svm import LinearSVC
from sklearn.exceptions import NotFittedError
import numpy as np


def preprocess(X, y):
    K = len(np.unique(y))
    N = len(X)
    Nk = np.bincount(y)

    X1 = np.repeat(X, N, 0)
    X2 = np.tile(X.T, N).T

    y1 = np.repeat(y, N)
    y2 = np.tile(y, N)

    yy = (y1 > y2).astype(int)

    # remove y1 == y2
    diff = y1 != y2
    X1 = X1[diff]
    X2 = X2[diff]
    yy = yy[diff]

    pairs = K*(K-1)
    ww = len(X1) / (pairs * (Nk[y1[diff]]*Nk[y2[diff]]))
    return X1-X2, yy, ww


def LinearSVM(C, random_state):
    return LinearSVC(C=C, fit_intercept=False, penalty='l1', tol=1e-3, dual=False, random_state=random_state)


class RankSVM(BaseEstimator, RegressorMixin):
    def __init__(self, C=1.0, random_state=None):
        self.C = C
        self.random_state=random_state
        self.coefs = None
        self._fitted = False

    def fit(self, X, y):
        self.classes_ = np.unique(y)  # required by sklearn
        estimator = LinearSVM(self.C, self.random_state)
        dX, dy, _ = preprocess(X, y)
        estimator.fit(dX, dy)
        self.coefs = estimator.coef_[0]
        self._fitted = True
        return self

    def predict(self, X):
        if not self._fitted:
            raise NotFittedError
        return np.sum(self.coefs * X, 1)
