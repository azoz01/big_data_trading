from ..ml.features.features import calculate_features_stream
from ..ml.model.serve import predict_online
from ..sources.news import get_news_sentiment_aggregates_from_redis
from ..sources.tickers import get_tickers_stream
from ..sources.transactions import get_transactions_stream
from ..utils import get_or_create_spark_session
from .process_registry import process_registry


@process_registry("online_ml")
class OnlineMlProcess:

    def execute(self):
        spark = get_or_create_spark_session()
        tickers_stream = get_tickers_stream(spark)
        transactions_stream = get_transactions_stream(spark)
        news_sentiments_df = get_news_sentiment_aggregates_from_redis(spark)
        features = calculate_features_stream(
            tickers_stream, transactions_stream, news_sentiments_df
        )
        features_with_prediction = predict_online(features).drop("features")
        features_with_prediction.writeStream.outputMode("append").format("console").options(
            truncate=False
        ).start().awaitTermination()
