from nltk.sentiment.vader import SentimentIntensityAnalyzer
from pyspark.sql import DataFrame, GroupedData
from pyspark.sql.functions import avg, col, max, min, std, udf
from pyspark.sql.types import StringType


def sentiment_analyzer(text: str) -> float:
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return scores["compound"]


sentiment_udf = udf(sentiment_analyzer, StringType())


def calculate_sentiment_aggregates(grouped_data: GroupedData) -> DataFrame:
    return grouped_data.agg(
        avg(col("sentiment")).alias("avg_sentiment"),
        std(col("sentiment")).alias("std_sentiment"),
        max(col("sentiment")).alias("max_sentiment"),
        min(col("sentiment")).alias("min_sentiment"),
    )
