import nltk
from pyspark.sql.functions import col

from ..ml.sentiment import calculate_sentiment_aggregates, sentiment_udf
from ..sources.news import get_newest_news_snapshot
from ..utils import get_or_create_spark_session
from .process_registry import process_registry

nltk.download("vader_lexicon")


@process_registry("news_to_redis")
class NewsToRedis:

    def execute(self):
        spark = get_or_create_spark_session()
        news = get_newest_news_snapshot(spark).coalesce(5)
        news = news.select(
            col("source"), col("headline"), sentiment_udf(col("headline")).alias("sentiment")
        )
        news_aggregates = calculate_sentiment_aggregates(news.groupBy("source"))
        news_aggregates.write.mode("overwrite").format("org.apache.spark.sql.redis").option(
            "table", "sentiments_aggregates"
        ).save()
