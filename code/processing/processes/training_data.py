from ..constants import FULL_TRAINING_DATA_TABLE, TRAINING_DATA_SCHEMA
from ..ml.features.features import calculate_features_df
from ..sources.news import get_news_history
from ..sources.tickers import get_tickers_history
from ..sources.transactions import get_transactions_history
from ..utils import ensure_schema_exists, get_or_create_spark_session
from .process_registry import process_registry


@process_registry("training_data")
class TrainingDataProcess:

    def execute(self):
        spark = get_or_create_spark_session()
        tickers_history = get_tickers_history(spark)
        transactions_history = get_transactions_history(spark)
        news_history = get_news_history(spark)
        features = calculate_features_df(tickers_history, transactions_history, news_history)
        ensure_schema_exists(TRAINING_DATA_SCHEMA)
        features.write.mode("overwrite").saveAsTable(
            f"{TRAINING_DATA_SCHEMA}.{FULL_TRAINING_DATA_TABLE}"
        )
