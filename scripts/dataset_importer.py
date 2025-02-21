import json
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

import polars as pl
from clickhouse_driver import Client


@dataclass
class BaseImporter:
    client: Client

    def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in ClickHouse."""
        query = f"SHOW TABLES LIKE '{table_name}'"
        result = self.client.execute(query)
        return len(result) > 0

    def create_table(self, table_name: str, ddl: str) -> None:
        """Create a table in ClickHouse."""
        self.client.execute(ddl)
        print(f"Created table {table_name}")

    def drop_table(self, table: str):
        """Drop a table from ClickHouse."""
        query = f"DROP TABLE IF EXISTS {table}"
        self.client.execute(query)
        print(f"Dropped table {table}")

    def import_dataset(self, df: pl.DataFrame, table: str):
        """
        Import a Polars DataFrame into ClickHouse using bulk insert.

        Args:
            df: Input DataFrame
            table: Target table name
        """
        data = [tuple(str(val) for val in row) for row in df.to_numpy()]
        self.client.execute(f"INSERT INTO {table} VALUES", data, types_check=True)
        print(f"Inserted {len(df)} rows into {table}")


@dataclass
class ClickHouseImporter(BaseImporter):
    """Class for importing datasets into ClickHouse with support for multiple file formats."""

    client: Client
    dataset_path: str | None
    supported_formats: dict[str, callable] = None
    filter_tables: list[str] = ["train_fraud_labels"]
    full_refresh: bool = False

    def __post_init__(self):
        """Initialize supported file formats."""
        self.supported_formats = {
            "csv": pl.read_csv,
            "json": pl.read_json,
            "parquet": pl.read_parquet,
        }

    def get_dataframe(
        self, dataset_path: str, dataset_type: str, interpolation: bool = False
    ) -> pl.DataFrame:
        """
        Read the dataset into a Polars DataFrame.

        Args:
            dataset_path: Path to the dataset file
            dataset_type: Type of the dataset file (csv, json, parquet)
            interpolation: Whether to perform special handling for interpolated data

        Returns:
            pl.DataFrame containing the dataset

        Raises:
            ValueError: If the file type is not supported
        """
        if dataset_type not in self.supported_formats:
            raise ValueError(f"Unsupported file type: {dataset_type}")

        try:
            if interpolation:
                with open(dataset_path, "r") as f:
                    data = json.load(f)
                    return pl.DataFrame(
                        {"code": list(data.keys()), "name": list(data.values())}
                    )
            return self.supported_formats[dataset_type](dataset_path)
        except Exception as e:
            raise RuntimeError(f"Failed to read dataset: {str(e)}")

    def get_file_type(self, dataset_path: str) -> str:
        """
        Determine the type of the dataset file.

        Args:
            dataset_path: Path to the dataset file

        Returns:
            File extension as string
        """
        return Path(dataset_path).suffix.lstrip(".")

    def get_columns_from_df(self, df: pl.DataFrame) -> str:
        """
        Generate ClickHouse column definitions from DataFrame schema.

        Args:
            df: Input DataFrame

        Returns:
            String of comma-separated column definitions
        """
        type_mapping = {
            pl.Int32: "Int32",
            pl.Float32: "Float32",
            pl.Utf8: "String",
            pl.Datetime: "DateTime",
        }

        ddl = []
        for column in df.columns:
            col_type = df.schema[column]
            if col_type in type_mapping:
                ddl.append(f"{column} {type_mapping[col_type]}")
            else:
                ddl.append(f"{column} String")  # Default to String for unknown types
        return ", ".join(ddl)

    def generate_clickhouse_ddl(self, df: pl.DataFrame, table_name: str) -> str:
        """
        Generate a ClickHouse DDL statement from a Polars DataFrame.

        Args:
            df: Input DataFrame
            table_name: Name of the table to create

        Returns:
            DDL statement as string
        """
        columns = self.get_columns_from_df(df)
        return f"CREATE TABLE {table_name} ({columns}) ENGINE = Memory"

    def get_datasets(self) -> dict[str, pl.DataFrame]:
        """
        Main execution method to process all datasets.

        Returns:
            Dictionary of table names and their corresponding DataFrames
        """
        base_path = Path.cwd().parent
        if not self.dataset_path:
            data_path = base_path / "datasets" / "financial"
        else:
            data_path = Path(self.dataset_path)

        if not data_path.exists():
            raise FileNotFoundError(f"Data directory not found: {data_path}")

        df_datasets = {}
        for path in data_path.rglob("*"):
            if path.is_file():
                table_name = path.stem
                file_type = self.get_file_type(path)

                try:
                    interpolation = table_name == "mcc_codes"
                    dataset = self.get_dataframe(str(path), file_type, interpolation)
                    df_datasets[table_name] = dataset
                    ddl = self.generate_clickhouse_ddl(dataset, table_name)
                    print(f"Generated DDL for {table_name}:\n{ddl}\n")
                except Exception as e:
                    print(f"Error processing {table_name}: {str(e)}")
                    continue

        return df_datasets

    def main(self) -> None:
        """Process and import datasets to ClickHouse."""
        for table_name, df in self.get_datasets().items():
            if self.full_refresh:
                self.drop_table(table_name)
            if not self.check_table_exists(table_name):
                self.create_table(
                    table_name, self.generate_clickhouse_ddl(df, table_name)
                )
            if table_name not in self.filter_tables:
                self.import_dataset(df, table_name)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--dataset", type=str, required=False)
    parser.add_argument("--full-refresh", action="store_true")
    args = parser.parse_args()

    client = Client("localhost", port=9000, user="clickhouse", password="clickhouse")
    importer = ClickHouseImporter(client, args.dataset, full_refresh=args.full_refresh)
    importer.main()
