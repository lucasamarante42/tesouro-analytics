import os
import requests
import pandas as pd
from datetime import datetime
from app.celery_app import app
from app.tasks.analyze_data import analyze_dataframe
from app.utils.metrics import metrics

DATA_DIR = os.getenv("DATA_DIR", "/data")
RAW_CSV = os.path.join(DATA_DIR, "raw.csv")

@app.task(name="app.tasks.fetch_data.fetch_and_process")
def fetch_and_process(csv_url: str = None):
	"""
	Baixa o CSV público (ou lê local se csv_url for caminho local),
	salva em /data/raw.csv e aciona a análise.
	"""
	os.makedirs(DATA_DIR, exist_ok=True)

	# se não passar url, tenta variável de ambiente ou usa arquivo local (se existir)
	csv_url = csv_url or os.getenv("CSV_URL")

	if csv_url and (csv_url.startswith("http://") or csv_url.startswith("https://")):
		resp = requests.get(csv_url, timeout=30)
		resp.raise_for_status()
		content = resp.content
		with open(RAW_CSV, "wb") as f:
			f.write(content)
	elif csv_url and os.path.exists(csv_url):
		# caminho local fornecido
		with open(csv_url, "rb") as fin, open(RAW_CSV, "wb") as fout:
			fout.write(fin.read())
	else:
		# tenta usar arquivo raw.csv já existente
		if not os.path.exists(RAW_CSV):
			raise FileNotFoundError("Nenhum CSV encontrado. Configure CSV_URL ou coloque data/raw.csv")
		# else: prosseguir

	# ler CSV com pandas (pt-BR format: ; separador e , decimal)
	df = pd.read_csv(RAW_CSV, sep=";", decimal=",", dayfirst=True, parse_dates=["Data Venda"], infer_datetime_format=True)
	# Garantir colunas padronizadas
	df.columns = [c.strip() for c in df.columns]

	# registra métrica
	metrics['last_fetch_timestamp'] = datetime.utcnow().timestamp()
	metrics['last_records_count'] = len(df)

	# chama análise (síncrono aqui; poderia ser outra task)
	return analyze_dataframe(df)
