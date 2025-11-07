import os
import json
from app.celery_app import app
from app.utils.email_client import send_email
from datetime import datetime
DATA_DIR = os.getenv("DATA_DIR", "/data")
REPORT_PATH = os.path.join(DATA_DIR, "report.json")

@app.task(name="app.tasks.send_email.send_weekly_report")
def send_weekly_report(to_address: str = None):
	"""
	Lê report.json e envia por e-mail o resumo.
	"""
	to_address = to_address or os.getenv("REPORT_TO_EMAIL")
	if not os.path.exists(REPORT_PATH):
		return {"status": "no_report"}

	with open(REPORT_PATH, "r", encoding="utf-8") as f:
		report = json.load(f)

	subject = f"Relatório Tesouro Direto - {datetime.utcnow().date().isoformat()}"
	body = []
	body.append(f"Gerado em: {report.get('generated_at')}")
	body.append(f"Total Geral processado: R$ {report.get('total_geral'):,}")
	body.append(f"Média diária (últimos 7 dias): R$ {report.get('last_7_mean'):,}")
	body.append(f"Média diária (últimos 30 dias): R$ {report.get('last_30_mean'):,}")
	body.append(f"Estimativa vendas próximos 7 dias: R$ {report.get('est_next_7'):,}")
	body.append("\nTop3 títulos por volume:")
	for k, v in report.get("top3", {}).items():
		body.append(f"- {k}: R$ {v:,}")

	body_text = "\n".join(body)

	if not to_address:
		# fallback: apenas log no console
		print("===== RELATÓRIO SEMANAL =====")
		print(body_text)
		print("============================")
		return {"status": "logged"}

	send_email(to_address=to_address, subject=subject, body=body_text)
	return {"status": "sent", "to": to_address}
