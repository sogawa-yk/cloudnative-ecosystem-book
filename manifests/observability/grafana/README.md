# Grafana

Grafana is included as part of the kube-prometheus-stack Helm chart.

See `../prometheus/values.yaml` for Grafana configuration under the `grafana:` key.

## Access

After installing kube-prometheus-stack, access Grafana via:

```bash
kubectl port-forward svc/prometheus-grafana 3000:80 -n book-observability
```

Default credentials: admin / admin
