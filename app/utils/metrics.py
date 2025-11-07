# simples dicionário in-memory para métricas básicas
# além disso, main.py expõe metricas ao Prometheus via prometheus_client
metrics = {
	"last_fetch_timestamp": None,
	"last_records_count": 0,
	"last_analysis": None,
	"last_total": 0,
	"last_est_next_7": 0
}
