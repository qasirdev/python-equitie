from pathlib import Path

import pandas as pd

from backend.logging_config import logger


class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.investors = pd.DataFrame()
        self.portfolio_companies = pd.DataFrame()
        self.deals = pd.DataFrame()
        self.allocations = pd.DataFrame()
        self.valuations = pd.DataFrame()
        self.capital_calls = pd.DataFrame()
        self.fees = pd.DataFrame()
        self.distributions = pd.DataFrame()
        self.statement_lines = pd.DataFrame()
        self.fx_rates = pd.DataFrame()

    def _load_csv(self, filename: str) -> pd.DataFrame:
        file_path = self.data_dir / filename
        if file_path.exists():
            try:
                return pd.read_csv(file_path)
            except Exception as e:
                logger.error(f"Failed to load {filename}", exc_info=e)
                return pd.DataFrame()
        else:
            logger.warning(f"File {filename} not found in {self.data_dir}")
            return pd.DataFrame()

    def load_all(self) -> None:
        logger.info("Loading all CSV files into DataFrames...")
        self.investors = self._load_csv("investors.csv")
        self.portfolio_companies = self._load_csv("portfolio_companies.csv")
        self.deals = self._load_csv("deals.csv")
        self.allocations = self._load_csv("allocations.csv")
        self.valuations = self._load_csv("valuations.csv")
        self.capital_calls = self._load_csv("capital_calls.csv")
        self.fees = self._load_csv("fees.csv")
        self.distributions = self._load_csv("distributions.csv")
        self.statement_lines = self._load_csv("statement_lines.csv")
        self.fx_rates = self._load_csv("fx_rates.csv")
        logger.info("CSV files loaded successfully.")


# Assuming the server is run from the `python-equitie` directory
data_store = DataLoader("data")
