import os
import json
from flask import Flask, jsonify, send_file, request, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest, CONTENT_TYPE_LATEST
from app.utils.metrics import metrics
from app.utils.mongo_client import get_last_report, get_mongo
from bson import ObjectId
from app.celery_app import celery_app

app = Flask(__name__)
DATA_DIR = os.getenv("DATA_DIR", "/data")
REPORT_PATH = os.path.join(DATA_DIR, "report.json")

# Metrics registry
g_last_total = Gauge('tesouro_last_total', 'Último total processado')
g_last_est = Gauge('tesouro_last_est_next_7', 'Estimativa vendas próximos 7 dias')

@app.route("/report")
def report():
	report = get_last_report()
	if not report:
		return jsonify({"error": "report not found"}), 404
	# converter ObjectId para string e remover metadados Mongo
	report["_id"] = str(report["_id"])
	return jsonify(report)

@app.route("/history")
def history():
	"""
	Retorna os últimos relatórios salvos no MongoDB.
	Query param opcional: ?limit=10
	"""
	limit = int(request.args.get("limit", 10))
	db = get_mongo()
	cursor = db.reports.find().sort("created_at", -1).limit(limit)

	history_list = []
	for doc in cursor:
		doc["_id"] = str(doc["_id"])
		doc["created_at"] = doc["created_at"].isoformat() + "Z"
		history_list.append(doc)

	return jsonify(history_list)

@app.route("/metrics")
def metrics_endpoint():
	db = get_mongo()
	# Pega o último relatório salvo
	report = db.reports.find_one(sort=[("created_at", -1)])

	if report:
		# garante que os valores são float
		last_total = float(report.get("total_geral", 0))
		est_next_7 = float(report.get("est_next_7", 0))

		g_last_total.set(last_total)
		g_last_est.set(est_next_7)

	return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/trigger", methods=["POST"])
def trigger():
	"""
	Dispara manualmente uma nova análise Celery.
	Opcionalmente, pode receber ?csv_url=... para usar outro CSV.
	"""
	csv_url = request.args.get("csv_url") or os.getenv("CSV_URL")
	if not csv_url:
		return jsonify({"error": "CSV_URL not configured"}), 400

	# Enfileira a tarefa Celery para processamento assíncrono
	task = celery_app.send_task("tasks.run_analysis", kwargs={"csv_url": csv_url})

	return jsonify({
		"message": "Task enviada para processamento",
		"csv_url": csv_url,
		"task_id": task.id
	})

if __name__ == "__main__":
	port = int(os.getenv("APP_PORT", "5000"))
	app.run(host="0.0.0.0", port=port)
