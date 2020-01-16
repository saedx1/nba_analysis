"""
This module holds a baseline model
"""
import numpy as np
import sklearn.metrics as sk_metrics
from .learner import MatchModel


class BaselineModel(MatchModel):
    """
    The baseline model predicts the number of points to be scored by a team based
    on the average in the last N games.
    """

    def __init__(self, n=10):
        self.n = n

    def fit(self, x, y):
        pass

    def predict(self, x):
        x = np.asanyarray(x)
        if x.ndim != 2:
            raise ValueError(
                "Passed array should have 2 dimensions (Sequences, Samples)"
            )

        if x.shape[1] != self.n:
            raise ValueError(f"Each sequence should have {self.n} samples in it")

        y_pred = []

        for i in x:
            y_pred.append(i.mean())

        return np.asanyarray(y_pred)

    def score(self, y_true, y_pred, metric=sk_metrics.mean_absolute_error):
        return metric(y_true, y_pred)
