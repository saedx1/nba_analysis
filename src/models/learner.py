from abc import ABC, abstractmethod
import keras


class MatchModel(ABC):
    @abstractmethod
    def fit(self, X, y):
        pass

    @abstractmethod
    def predict(self, X):
        pass
