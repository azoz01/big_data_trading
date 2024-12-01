from pyspark.sql import Window
from pyspark.sql.functions import col, unix_timestamp, window

from ...utils import get_or_create_spark_session

get_or_create_spark_session()  # Without this call there is error with uninitialized spark context

LAST_HOUR_WINDOW = Window.orderBy(unix_timestamp(col("timestamp"))).rangeBetween(-3600, -1)

LAST_HOUR_STREAMING_WINDOW = window(col("timestamp"), "1 hour", "1 second")

LAST_HALF_DAY_WINDOW = Window.orderBy(unix_timestamp(col("timestamp"))).rangeBetween(-12 * 3600, -1)

LAST_HALF_DAY_STREAMING_WINDOW = window(col("timestamp"), "12 hours", "1 second")

LAST_DAY_WINDOW = Window.orderBy(unix_timestamp(col("timestamp"))).rangeBetween(-24 * 3600, -1)

LAST_DAY_STREAMING_WINDOW = window(col("timestamp"), "24 hours", "1 second")
