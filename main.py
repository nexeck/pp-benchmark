import argparse
from datetime import datetime, timedelta
import decimal
import glob
import logging
import logging.config
import re
import pandas as pd
import yfinance as yf

class Validator(object):

    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def __call__(self, value):
        if not self._pattern.match(value):
            raise argparse.ArgumentTypeError(
                "Argument has to match '{}'".format(self._pattern.pattern))
        return value

def main(args):
    benchmarks = []
    totalRatio = 0
    for benchmark in args.benchmark:
        benchmark = benchmark.split(":")
        ticker = benchmark[0]
        ratio = float(benchmark[1])

        benchmarkData = yf.Ticker(ticker)
        benchmarkHistory = benchmarkData.history(period="max", interval="1d")

        totalRatio += ratio

        benchmarks.append({
                'ticker': benchmarkData.ticker,
                'shortName': benchmarkData.info['shortName'],
                'ratio': ratio,
                'history': benchmarkHistory
                })

    if totalRatio != 100:
        raise Exception("Total ratio %s <> 100" % totalRatio)

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

            for benchmark in benchmarks:
                history_row = getHistory(benchmark['history'], transactionDate)

                value = row["Value"] / 100 * benchmark['ratio']
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
                        "Ticker Symbol": benchmark['ticker'],
                        "Security Name": "Benchmark - %s" % benchmark['shortName']
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

    benchmarkType = Validator(r"^[A-Z0-9]+(\.[A-Z]+)?:\d+$")

    parser = argparse.ArgumentParser()

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--input", default=None, help="Path to one transactions file")
    input_group.add_argument(
        "--input-dir", default=None, help="Path to directory with transaction files"
    )

    parser.add_argument(
        "--benchmark", action="append", type=benchmarkType, help="Benchmark ticker"
    )

    parser.add_argument("--output", required=True, help="Output CSV file")
    args = parser.parse_args()
    main(args)
