# PP Benchmark

## Usage

Export Portfolio Performance security account transactions as CSV

For a single csv file

```sh
make run ARGS="--input .tmp/test/ING.csv --output .tmp/out.csv --benchmark VWCE.DE:100"
```

For multiple csv files (Export of multiple security accounts)

FTSE All World Benchmark

```sh
make run ARGS="--input-dir .tmp/test --output .tmp/out.csv --benchmark VWCE.DE:100"
```

70:30 Benchmark

```sh
make run ARGS="--input-dir .tmp/test --output .tmp/out.csv --benchmark EUNL.DE:70 --benchmark IS3N.DE:30"
```

nexeck Core Benchmark

```sh
make run ARGS="--input-dir .tmp/test --output .tmp/out.csv --benchmark JPGL.DE:28 --benchmark XDEM.DE:23.8 --benchmark CEMR.DE:14 --benchmark AYEM.DE:30 --benchmark IUSN.DE:4.2"
```

Create separate deposit/security account in PP and import the output file.
