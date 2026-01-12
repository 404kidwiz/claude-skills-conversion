"""
ETL Pipeline Automation
Automated ETL pipeline with error handling and monitoring
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import json
import time

try:
    import pandas as pd
    import schedule
except ImportError:
    raise ImportError("pandas and schedule required: pip install pandas schedule")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    name: str
    schedule_interval: str  # "daily", "hourly", "minutes:30"
    source_type: str  # "csv", "api", "database"
    source_config: Dict[str, Any]
    destination_type: str  # "csv", "database", "s3"
    destination_config: Dict[str, Any]
    transformations: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'PipelineConfig':
        return cls(**config)


@dataclass
class PipelineRun:
    pipeline_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    records_processed: int = 0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ETLPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.history: List[PipelineRun] = []

    def extract(self) -> pd.DataFrame:
        logger.info(f"Extracting data from {self.config.source_type}")

        if self.config.source_type == "csv":
            df = self._extract_csv()
        elif self.config.source_type == "api":
            df = self._extract_api()
        elif self.config.source_type == "database":
            df = self._extract_database()
        else:
            raise ValueError(f"Unknown source type: {self.config.source_type}")

        logger.info(f"Extracted {len(df)} records")
        return df

    def _extract_csv(self) -> pd.DataFrame:
        filepath = self.config.source_config.get('filepath')
        return pd.read_csv(filepath)

    def _extract_api(self) -> pd.DataFrame:
        import requests

        url = self.config.source_config.get('url')
        params = self.config.source_config.get('params', {})

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return pd.DataFrame(data)

    def _extract_database(self) -> pd.DataFrame:
        import sqlalchemy

        connection_string = self.config.source_config.get('connection_string')
        query = self.config.source_config.get('query')

        engine = sqlalchemy.create_engine(connection_string)
        return pd.read_sql(query, engine)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        logger.info("Transforming data")

        transformations = self.config.transformations or []

        for transformation in transformations:
            df = self._apply_transformation(df, transformation)

        logger.info(f"Transformed data: {len(df)} records")
        return df

    def _apply_transformation(self, df: pd.DataFrame, transformation: Dict[str, Any]) -> pd.DataFrame:
        transform_type = transformation['type']

        if transform_type == "filter":
            df = self._transform_filter(df, transformation)
        elif transform_type == "rename":
            df = self._transform_rename(df, transformation)
        elif transform_type == "aggregate":
            df = self._transform_aggregate(df, transformation)
        elif transform_type == "add_column":
            df = self._transform_add_column(df, transformation)
        elif transform_type == "drop_columns":
            df = self._transform_drop_columns(df, transformation)
        elif transform_type == "deduplicate":
            df = self._transform_deduplicate(df, transformation)
        elif transform_type == "fill_nulls":
            df = self._transform_fill_nulls(df, transformation)
        else:
            logger.warning(f"Unknown transformation type: {transform_type}")

        return df

    def _transform_filter(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        column = config['column']
        operator = config['operator']
        value = config['value']

        if operator == 'eq':
            return df[df[column] == value]
        elif operator == 'ne':
            return df[df[column] != value]
        elif operator == 'gt':
            return df[df[column] > value]
        elif operator == 'lt':
            return df[df[column] < value]
        elif operator == 'contains':
            return df[df[column].str.contains(value, na=False)]
        else:
            return df

    def _transform_rename(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        columns_map = config['mapping']
        return df.rename(columns=columns_map)

    def _transform_aggregate(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        group_by = config['group_by']
        aggregations = config['aggregations']

        return df.groupby(group_by).agg(aggregations).reset_index()

    def _transform_add_column(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        column_name = config['name']
        expression = config['expression']

        if expression == 'timestamp':
            df[column_name] = datetime.now()
        elif expression == 'year':
            df[column_name] = df[config['source_column']].dt.year
        elif expression == 'month':
            df[column_name] = df[config['source_column']].dt.month
        elif expression == 'calculated':
            df[column_name] = df[config['source_column1']] + df[config['source_column2']]
        else:
            df[column_name] = expression

        return df

    def _transform_drop_columns(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        columns_to_drop = config['columns']
        return df.drop(columns=columns_to_drop)

    def _transform_deduplicate(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        subset = config.get('subset')
        keep = config.get('keep', 'first')
        return df.drop_duplicates(subset=subset, keep=keep)

    def _transform_fill_nulls(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        strategy = config['strategy']
        columns = config.get('columns', df.columns)

        if strategy == 'mean':
            df[columns] = df[columns].fillna(df[columns].mean())
        elif strategy == 'median':
            df[columns] = df[columns].fillna(df[columns].median())
        elif strategy == 'mode':
            df[columns] = df[columns].fillna(df[columns].mode().iloc[0])
        elif strategy == 'constant':
            value = config['value']
            df[columns] = df[columns].fillna(value)
        elif strategy == 'forward':
            df[columns] = df[columns].fillna(method='ffill')
        elif strategy == 'backward':
            df[columns] = df[columns].fillna(method='bfill')

        return df

    def load(self, df: pd.DataFrame):
        logger.info(f"Loading data to {self.config.destination_type}")

        if self.config.destination_type == "csv":
            self._load_csv(df)
        elif self.config.destination_type == "database":
            self._load_database(df)
        elif self.config.destination_type == "s3":
            self._load_s3(df)
        else:
            raise ValueError(f"Unknown destination type: {self.config.destination_type}")

        logger.info(f"Loaded {len(df)} records")

    def _load_csv(self, df: pd.DataFrame):
        filepath = self.config.destination_config.get('filepath')
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filepath, index=False)

    def _load_database(self, df: pd.DataFrame):
        import sqlalchemy

        connection_string = self.config.destination_config.get('connection_string')
        table_name = self.config.destination_config.get('table_name')

        engine = sqlalchemy.create_engine(connection_string)
        df.to_sql(table_name, engine, if_exists='append', index=False)

    def _load_s3(self, df: pd.DataFrame):
        import boto3

        bucket = self.config.destination_config.get('bucket')
        key = self.config.destination_config.get('key')

        csv_buffer = df.to_csv(index=False)

        s3 = boto3.client('s3')
        s3.put_object(Bucket=bucket, Key=key, Body=csv_buffer)

    def run(self, on_success: Optional[Callable] = None, on_failure: Optional[Callable] = None):
        run = PipelineRun(
            pipeline_name=self.config.name,
            start_time=datetime.now()
        )

        try:
            # Extract
            df = self.extract()

            # Transform
            df = self.transform(df)

            # Load
            self.load(df)

            run.records_processed = len(df)
            run.end_time = datetime.now()
            run.status = "completed"

            if on_success:
                on_success(run)

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            run.errors.append(str(e))
            run.end_time = datetime.now()
            run.status = "failed"

            if on_failure:
                on_failure(run)

        finally:
            self.history.append(run)
            self._log_run(run)

    def _log_run(self, run: PipelineRun):
        log_file = Path(f"./pipeline_logs/{self.config.name}.json")
        log_file.parent.mkdir(parents=True, exist_ok=True)

        history = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                history = json.load(f)

        history.append({
            'pipeline_name': run.pipeline_name,
            'start_time': run.start_time.isoformat(),
            'end_time': run.end_time.isoformat() if run.end_time else None,
            'status': run.status,
            'records_processed': run.records_processed,
            'errors': run.errors
        })

        with open(log_file, 'w') as f:
            json.dump(history, f, indent=2)

    def schedule(self):
        interval = self.config.schedule_interval

        if interval == "daily":
            schedule.every().day.at("00:00").do(self.run)
        elif interval == "hourly":
            schedule.every().hour.do(self.run)
        elif interval.startswith("minutes:"):
            minutes = int(interval.split(":")[1])
            schedule.every(minutes).minutes.do(self.run)

        logger.info(f"Scheduled pipeline {self.config.name} to run {interval}")

        while True:
            schedule.run_pending()
            time.sleep(60)


def main():
    config = PipelineConfig(
        name="sales_pipeline",
        schedule_interval="daily",
        source_type="csv",
        source_config={"filepath": "./data/sales.csv"},
        destination_type="csv",
        destination_config={"filepath": "./output/sales_processed.csv"},
        transformations=[
            {
                "type": "filter",
                "column": "status",
                "operator": "eq",
                "value": "completed"
            },
            {
                "type": "rename",
                "mapping": {"customer_id": "customer", "order_date": "date"}
            },
            {
                "type": "add_column",
                "name": "processed_at",
                "expression": "timestamp"
            }
        ]
    )

    pipeline = ETLPipeline(config)
    pipeline.run()


if __name__ == "__main__":
    main()
