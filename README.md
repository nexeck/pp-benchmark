# PP Benchmark

## Usage

Export Portfolio Performance security account transactions as CSV.

```sh
make run ARGS="--input .tmp/FIRE.csv --output .tmp/out.csv"
```

For multiple csv files (Export of multiple security accounts)

```sh
make run ARGS="--input-dir .tmp/test --output .tmp/out.csv --benchmark VWCE.DE:100"
```

For multiple benchmark securities

```sh
make run ARGS="--input-dir .tmp/test --output .tmp/out.csv --benchmark EUNL.DE:70 --benchmark IS3N.DE:30"
```

Create separate deposit/security account in PP and import the output file.
