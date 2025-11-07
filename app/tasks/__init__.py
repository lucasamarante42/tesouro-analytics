from app.celery_app import celery_app
from app.tasks.analyze_data import analyze_dataframe
import pandas as pd
import requests
import os

@celery_app.task(name="tasks.run_analysis")
def run_analysis(csv_url=None):
	"""
	Task principal para baixar o CSV, processar e salvar no MongoDB.
	Pode ser chamada manualmente pelo endpoint /trigger.
	"""
	url = csv_url or os.getenv("CSV_URL")
	data_dir = os.getenv("DATA_DIR", "/data")
	csv_path = os.path.join(data_dir, "dados.csv")

	try:
		# Download do CSV público
		resp = requests.get(url)
		resp.raise_for_status()
		with open(csv_path, "wb") as f:
			f.write(resp.content)

		df = pd.read_csv(csv_path, sep=";")
		report = analyze_dataframe(df)
		return {"status": "ok", "report": report}
	except Exception as e:
		return {"status": "error", "message": str(e)}
