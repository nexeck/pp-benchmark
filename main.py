import argparse
from datetime import datetime, timedelta
import logging
import logging.config
import pandas as pd
import yfinance as yf


def main(args):
    benchmark = yf.Ticker(args.benchmark)
    benchmarkHistory = benchmark.history(period="max")

    transactions = pd.read_csv(args.input, sep=";", index_col="Date", thousands=".", decimal=",")

    rows_list = []
    for index, row in transactions.iterrows():
        if isinstance(row["Ticker Symbol"], str):
            try:
                transactionDate = datetime.strptime(index, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                transactionDate = datetime.strptime(index, "%Y-%m-%dT%H:%M")

            transactionDate = transactionDate.replace(hour=0, minute=0, second=0)

            history_row = getHistory(benchmarkHistory, transactionDate)

            value = row['Value'] * -1
            price = history_row.iloc[0]['Close']
            shares = value / price

            transaction = {}
            transaction.update({
                'Date': transactionDate,
                'Type': row["Type"],
                'Value': value,
                'Transaction Currency': 'EUR',
                'Shares': shares,
                'Ticker Symbol': benchmark.ticker
                }
            )

            rows_list.append(transaction)

    benchmarkTransactions = pd.DataFrame(rows_list)
    benchmarkTransactions.to_csv(args.output, index=False, sep=";", decimal=",")

    print(benchmarkTransactions)


def getHistory(benchmark_history, transaction_date):
    result = None
    while result is None:
        try:
            transactionDateStr = transaction_date.strftime("%Y-%m-%d")
            result = benchmark_history.loc[[transactionDateStr]]
        except KeyError:
            transaction_date = transaction_date - timedelta(days=1)
            pass

    return result

if __name__ == "__main__":
    logging.basicConfig(
        format='%(levelname)s %(asctime)s %(message)s',
        level="INFO"
        )

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to transactions file")
    parser.add_argument("--benchmark", required=False, default="VWCE.DE", help="Benchmark ticker")
    parser.add_argument("--output", required=True, help="Output CSV file")
    args = parser.parse_args()
    main(args)
