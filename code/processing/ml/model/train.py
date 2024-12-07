from typing import Tuple

from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, max, to_date

from ...constants import FEATURES_VECTOR_COLUMN
from ...utils import convert_features_to_double_non_null
from .utils import FEATURES_ASSEMBLER


def train_test_split(df: DataFrame) -> Tuple[DataFrame, DataFrame]:
    df = df.withColumn("date", to_date(col("timestamp")))
    df = convert_features_to_double_non_null(df)
    latest_date = df.select(max(col("date")).alias("max_date")).collect()[0]["max_date"]
    train_df = df.filter(col("date") < latest_date)
    test_df = df.filter(col("date") == latest_date)
    return train_df, test_df


def train_evaluate_model(
    train_split: DataFrame, test_split: DataFrame
) -> Tuple[LogisticRegression, dict[str, float]]:
    train_split = FEATURES_ASSEMBLER.transform(train_split)
    model = LogisticRegression(featuresCol=FEATURES_VECTOR_COLUMN, labelCol="target")
    model = model.fit(train_split)
    evaluator = BinaryClassificationEvaluator(labelCol="target", metricName="areaUnderROC")
    train_metric = evaluator.evaluate(model.transform(train_split))
    test_metric = evaluator.evaluate(model.transform(FEATURES_ASSEMBLER.transform(test_split)))
    return model, {"train_metric": train_metric, "test_metric": test_metric}
