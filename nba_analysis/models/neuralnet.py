import sklearn.metrics as sk_metrics
from keras.layers import Input, Dense, Dropout, GRU, concatenate
from keras.models import Model

from .learner import MatchModel


class NeuralNetModel(MatchModel):
    """
    A neural network with a Feed-Forward network for aggregated data joined
    with a Recurrent network for sequential data (time-series) to predict the
    outcome of an NBA match.
    """

    def __init__(
        self, sequence_len: int, n_aggregated: int = 42, n_sequential: int = 21
    ):
        # FeedForward Neural Network
        home_input = Input((n_aggregated,))
        road_input = Input((n_aggregated,))
        home_dense = Dense(400, activation="tanh")(home_input)
        road_dense = Dense(400, activation="tanh")(road_input)
        home_dropout = Dropout(0.35)(home_dense)
        road_dropout = Dropout(0.35)(road_dense)
        agg_conc = concatenate([home_dropout, road_dropout])
        total_dense = Dense(900, activation="tanh")(agg_conc)
        total_dropout = Dropout(0.3)(total_dense)

        # Recurrent Neural Network
        home_sequence = Input((sequence_len, n_sequential))
        road_sequence = Input((sequence_len, n_sequential))
        home_rnn = (GRU(500, dropout=0.2, recurrent_dropout=0.1))(home_sequence)
        road_rnn = (GRU(500, dropout=0.2, recurrent_dropout=0.1))(road_sequence)
        agg_conc = concatenate([home_rnn, road_rnn])
        total_sequence = Dense(1000, activation="tanh")(agg_conc)

        # Final Concatenation
        final_conc = concatenate([total_dropout, total_sequence])
        output = Dense(2, activation="softmax")(final_conc)
        self.model = Model(
            [home_input, road_input, home_sequence, road_sequence], output
        )

    def compile_model(self, loss, optimizer, metrics=None):
        self.model.compile(loss=loss, optimizer=optimizer, metrics=metrics)

    def fit(
        self,
        x,
        y,
        epochs: int = 10,
        batch_size: int = 32,
        x_val=None,
        y_val=None,
        **kwargs
    ):
        self.model.fit(
            x,
            y,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(x_val, y_val),
            **kwargs
        )

    def predict(self, x):
        return self.model.predict(x)

    def score(self, y_true, y_pred, metric=sk_metrics.accuracy_score):
        return metric(y_true, y_pred)
