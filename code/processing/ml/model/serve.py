from pyspark.ml.classification import LogisticRegressionModel

from ...constants import MODEL_PATH


class OnlinePredictor:

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = LogisticRegressionModel.load(self.model_path)

    def __call__(self, input):
        return self.model.transform(input)


predict_online = OnlinePredictor(MODEL_PATH)
