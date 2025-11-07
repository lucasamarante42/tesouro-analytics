import os
from pymongo import MongoClient
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/tesourodb")
DB_NAME = os.getenv("MONGO_DB_NAME", "tesourodb")

_client = None

def get_mongo():
	global _client
	if _client is None:
		_client = MongoClient(MONGO_URI)
	return _client[DB_NAME]

def save_report(report: dict):
	"""
	Salva o relatório completo no MongoDB.
	"""
	db = get_mongo()
	report["created_at"] = datetime.utcnow()
	db.reports.insert_one(report)
	return True

def get_last_report():
	"""
	Retorna o último relatório salvo.
	"""
	db = get_mongo()
	doc = db.reports.find().sort("created_at", -1).limit(1)
	return next(doc, None)
