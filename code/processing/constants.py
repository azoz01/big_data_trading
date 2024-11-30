FEATURE_LIST = [
    "open_24h",
    "volume_24h",
    "low_24h",
    "high_24h",
    "volume_30d",
    "best_bid",
    "best_bid_size",
    "best_ask",
    "best_ask_size",
    "avg_price_last_hour",
    "avg_price_last_half_day",
    "avg_price_last_day",
    "transaction_count_last_hour",
    "transaction_count_last_half_day",
    "transaction_count_last_day",
    "coindesk_avg_sentiment",
    "coindesk_std_sentiment",
    "coindesk_max_sentiment",
    "coindesk_min_sentiment",
    "cointelegraph_avg_sentiment",
    "cointelegraph_std_sentiment",
    "cointelegraph_max_sentiment",
    "cointelegraph_min_sentiment",
    "cryptocurrency_news_avg_sentiment",
    "cryptocurrency_news_std_sentiment",
    "cryptocurrency_news_max_sentiment",
    "cryptocurrency_news_min_sentiment",
]

CRYPTO_NEWS_SOURCES = ["coindesk", "cointelegraph", "cryptocurrency_news"]

NEWS_COLUMNS = [
    "timestamp",
    "source",
    "headline",
]

TRAINING_DATA_SCHEMA = "training_data"
FULL_TRAINING_DATA_TABLE = "full_training_dataset"
