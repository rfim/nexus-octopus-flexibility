"""Illustrative Spark Silver transform; requires a Spark runtime."""

from pyspark.sql import DataFrame, Window, functions as F


def build_silver_events(bronze: DataFrame) -> DataFrame:
    typed = bronze.select(
        "event_id", "asset_id", "ingested_at",
        F.to_timestamp("event_time").alias("event_time"),
        F.col("power_kw").cast("double").alias("power_kw"),
    )
    invalid = typed.filter(
        F.col("event_id").isNull() | F.col("asset_id").isNull()
        | (F.trim(F.col("event_id")) == "") | (F.trim(F.col("asset_id")) == "")
        | F.col("event_time").isNull() | F.isnan("power_kw")
        | F.col("power_kw").isNull() | (F.abs(F.col("power_kw")) == float("inf"))
        | F.col("ingested_at").isNull()
    )
    if invalid.limit(1).count():
        raise ValueError("Bronze contains records that fail the Silver contract")
    newest = Window.partitionBy("event_id").orderBy(F.col("ingested_at").desc())
    return (typed.withColumn("_rank", F.row_number().over(newest))
            .filter(F.col("_rank") == 1).drop("_rank"))
