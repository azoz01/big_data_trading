from pyspark.ml.feature import VectorAssembler

from ...constants import FEATURE_LIST, FEATURES_VECTOR_COLUMN
from ...utils import get_or_create_spark_session

get_or_create_spark_session()  # Without this call there is error with uninitialized spark context

FEATURES_ASSEMBLER = VectorAssembler(inputCols=FEATURE_LIST, outputCol=FEATURES_VECTOR_COLUMN)
