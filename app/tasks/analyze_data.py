import json
import os
import numpy as np
import pandas as pd
from datetime import datetime
from app.utils.metrics import metrics
from app.utils.mongo_client import save_report  # <--- NOVO

DATA_DIR = os.getenv("DATA_DIR", "/data")
REPORT_PATH = os.path.join(DATA_DIR, "report.json")

def estimate_next_week(total_by_day: pd.Series):
	N = min(60, len(total_by_day))
	series = total_by_day.tail(N)
	if len(series) < 3:
		mean = series.mean() if len(series) > 0 else 0.0
		return mean * 7
	x = np.arange(len(series))
	y = series.values.astype(float)
	a, b = np.polyfit(x, y, 1)
	next_x = np.arange(len(series), len(series) + 7)
	preds = a * next_x + b
	preds = np.clip(preds, a_min=0, a_max=None)
	return float(preds.sum())

def analyze_dataframe(df: pd.DataFrame):
	df = df.copy()

	df.rename(columns={
		"Tipo Titulo": "tipo",
		"Vencimento do Titulo": "vencimento",
		"Data Venda": "data_venda",
		"PU": "pu",
		"Quantidade": "quantidade",
		"Valor": "valor"
	}, inplace=True)

	# vírgula para ponto
	df['valor'] = df['valor'].str.replace(',', '.', regex=False)
	df['quantidade'] = df['quantidade'].str.replace(',', '.', regex=False)

	# conversão de tipos
	df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
	df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')
	df['data_venda'] = pd.to_datetime(df['data_venda'], dayfirst=True, errors='coerce')

	# remover linhas com valores inválidos
	df.dropna(subset=['data_venda', 'valor'], inplace=True)

	total_por_titulo = df.groupby('tipo')['valor'].sum().sort_values(ascending=False)
	total_geral = total_por_titulo.sum()
	daily = df.groupby('data_venda')['valor'].sum().sort_index()

	last_7_mean = float(daily.tail(7).mean()) if len(daily) >= 1 else 0.0
	last_30_mean = float(daily.tail(30).mean()) if len(daily) >= 1 else 0.0
	est_next_7 = estimate_next_week(daily)
	top3 = total_por_titulo.head(3).to_dict()

	report = {
		"generated_at": datetime.utcnow().isoformat() + "Z",
		"total_geral": float(total_geral),
		"last_7_mean": last_7_mean,
		"last_30_mean": last_30_mean,
		"est_next_7": est_next_7,
		"top3": top3,
		"daily_points": [
			{"date": d.strftime("%Y-%m-%d"), "valor": float(v)} for d, v in daily.items()
		]
	}

	# salva em arquivo local
	os.makedirs(DATA_DIR, exist_ok=True)
	with open(REPORT_PATH, "w", encoding="utf-8") as f:
		json.dump(report, f, ensure_ascii=False, indent=2)

	# salva no MongoDB
	save_report(report)

	metrics['last_analysis'] = datetime.utcnow().timestamp()
	metrics['last_total'] = total_geral
	metrics['last_est_next_7'] = est_next_7

	return report
