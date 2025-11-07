from celery import Celery
import os

REDIS_BROKER = os.getenv("CELERY_BROKER_URL", "pyamqp://guest@rabbitmq//")  # default rabbitmq

celery_app = Celery("tesouro", broker=REDIS_BROKER, backend=None)

# caminho para tasks será app.tasks.*
# Foi comentado o beat_schedule
celery_app.conf.update(
	task_serializer="json",
	accept_content=["json"],
	result_serializer="json",
	timezone="America/Sao_Paulo",
	# beat_schedule={
	# 	# roda full pipeline a cada 2 dias (48 horas)
	# 	"run-every-2-days": {
	# 		"task": "app.tasks.fetch_data.fetch_and_process",
	# 		"schedule": 60 * 60 * 48,  # 48 horas em segundos
	# 	},
	# 	# envia relatório semanal (7 dias)
	# 	"send-weekly-report": {
	# 		"task": "app.tasks.send_email.send_weekly_report",
	# 		"schedule": 60 * 60 * 24 * 7,
	# 	},
	# },
)

# importa explicitamente as tasks para registrá-las
import app.tasks
