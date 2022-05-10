# Light GBM

To test locally:
```bash
docker build -t lightgbm .
docker run --rm --name lightgbm -v ~/.config:/root/.config -p 8000:80 -p 7999:79 -p 6000:6000 lightgbm:latest &
```

### REST request
```
curl -X POST -H 'Content-Type: application/json' -d '{"data": {"ndarray":[[1, 30,200,1,0]]}}' http://localhost:8000/predict
```
you output should look like

```
{"jsonData":{"data":{"names":[],"ndarray":[0.7627219473176108]}},"meta":{"metrics":[{"key":"seldon_run_time_histogram","tags":{"method":"predict","route":"REST","service":"my-model-name"},"type":"TIMER","value":14.751672744750977}]}}
```

### gRPC request
use -plaintext only for model hosted locally, remove the flag for model hosted on Barista.
```
grpcurl -plaintext  -d '{"data": {"ndarray":[[1, 30,200,1,0]]}}' -proto ./prediction.proto  -max-time 100 localhost:7999 seldon.protos.Seldon/Predict
```

you should get output like

```
{
  "status": {

  },
  "meta": {
    "metrics": [
      {
        "key": "seldon_run_time_histogram",
        "type": "TIMER",
        "value": 1.0972023, # this value is in milliseconds (though get exposed as seconds in prometheus)
        "tags": {
          "route": "GRPC",
          "service": "my-model-name"
        }
      }
    ]
  },
  "data": {
    "ndarray": [
        0.7627219473176108
      ]
  }
}
```

### For metrics:
```
curl localhost:6000/metrics
```
