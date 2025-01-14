from pyspark.ml.classification import LogisticRegressionModel


class OnlinePredictor:

    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = LogisticRegressionModel.load(self.model_path)

    def __call__(self, input):
        return self.model.transform(input)
