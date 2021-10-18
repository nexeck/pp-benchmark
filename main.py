import argparse
from datetime import datetime, timedelta
import glob
import logging
import logging.config
import pandas as pd
import yfinance as yf


def main(args):
    benchmark = yf.Ticker(args.benchmark)
    benchmarkHistory = benchmark.history(period="max")

    fileList = []
    transactionList = []
    if args.input:
        fileList.append(args.input)

    if args.input_dir:
        fileList = glob.glob(args.input_dir + "/*.csv")

    for filename in fileList:
        transactionList.append(
            pd.read_csv(filename, sep=";", thousands=".", decimal=",")
        )

    transactions = pd.concat(transactionList, axis=0, ignore_index=True)

    rows_list = []
    for _, row in transactions.iterrows():
        if isinstance(row["Ticker Symbol"], str):
            try:
                transactionDate = datetime.strptime(row["Date"], "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                transactionDate = datetime.strptime(row["Date"], "%Y-%m-%dT%H:%M")

            transactionDate = transactionDate.replace(hour=0, minute=0, second=0)

            history_row = getHistory(benchmarkHistory, transactionDate)

            value = row["Value"]
            price = history_row.iloc[0]["Close"]
            shares = value / price

            transaction = {}
            transaction.update(
                {
                    "Date": transactionDate,
                    "Type": getTransactionType(row["Type"]),
                    "Value": value,
                    "Transaction Currency": "EUR",
                    "Shares": shares,
                    "Ticker Symbol": benchmark.ticker,
                    "Security Name": "Benchmark - %s" % benchmark.info['shortName']
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

def getTransactionType(type: str) -> str:
    match type:
        case "Buy" | "Transfer (Inbound)" | "Delivery (Inbound)":
            return "Buy"
        case "Sell" | "Transfer (Outbound)" | "Delivery (Outbound)":
            return "Sell"
        case _:
            raise Exception("Unknown type %s" % type)

if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s %(asctime)s %(message)s", level="INFO")

    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", default=None, help="Path to one transactions file")
    group.add_argument(
        "--input-dir", default=None, help="Path to directory with transaction files"
    )

    parser.add_argument(
        "--benchmark", required=False, default="VWCE.DE", help="Benchmark ticker"
    )
    parser.add_argument("--output", required=True, help="Output CSV file")
    args = parser.parse_args()
    main(args)
