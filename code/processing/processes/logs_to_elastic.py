from pyspark.sql import DataFrame

from ..sources.tickers import get_tickers_history, process_tickers_to_elastic
from ..sources.transactions import (
    get_transactions_history,
    process_transactions_to_elastic,
)
from ..utils import get_or_create_spark_session
from .process_registry import process_registry


@process_registry("logs_to_elastic")
class LogsElasticProcess:

    def execute(self):
        spark = get_or_create_spark_session()
        transactions = process_transactions_to_elastic(get_transactions_history(spark))
        transactions.printSchema()
        self._write_df_to_elastic(transactions, "transactions")
        tickers = process_tickers_to_elastic(get_tickers_history(spark))
        tickers.printSchema()
        self._write_df_to_elastic(tickers, "tickers")

    def _write_df_to_elastic(self, df: DataFrame, index: str) -> None:
        df.write.option("es.mapping.id", "timestamp").option(
            "es.mapping.default.field", "text"
        ).option("es.mapping.dynamic", "true").format("org.elasticsearch.spark.sql").mode(
            "append"
        ).save(
            index
        )
