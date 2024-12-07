from ..constants import (
    FULL_TRAINING_DATA_TABLE,
    MODEL_PATH,
    TRAINING_DATA_SCHEMA,
)
from ..ml.model.train import train_evaluate_model, train_test_split
from ..utils import get_or_create_spark_session
from .process_registry import process_registry


@process_registry("model_training")
class ModelTrainingProcess:

    def execute(self):
        spark = get_or_create_spark_session()
        training_data = spark.read.table(f"{TRAINING_DATA_SCHEMA}.{FULL_TRAINING_DATA_TABLE}")
        train_split, test_split = train_test_split(training_data)
        model, metrics = train_evaluate_model(train_split, test_split)
        model.write().overwrite().save(MODEL_PATH)
        print(metrics)
