# PP Benchmark

## Usage

Export Portfolio Performance security account transactions as CSV.

```sh
make run ARGS="--input .tmp/FIRE.csv --output .tmp/out.csv"
```

For multiple csv files (Export of multiple security accounts)

```sh
make run ARGS="--input-dir .tmp/test --output .tmp/out.csv"
```

Create separate deposit/security account in PP and import the output file.
