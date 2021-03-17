# Guidance Pipeline
Guidance Pipeline take's the csv files guidances and output their respective parts in JSON.

# Usage
**Running the application**
```
go run . [OPTIONS] [ARGS] 

```

**Building the application**
```
go build .
```

**Running the compiled application**
```
./guidance_pipeline csv/[FILE]
```

**Running the test suite**
```
go test
```

**Updating the golden file to test against**
```
go test -update
```
