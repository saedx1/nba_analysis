from abc import ABC, abstractmethod


class MatchModel(ABC):
    """
    Represents the parent class of any model.
    """

    @abstractmethod
    def fit(self, x, y):
        pass

    @abstractmethod
    def predict(self, x):
        pass

    @abstractmethod
    def score(self, y_true, y_pred, metric):
        pass
