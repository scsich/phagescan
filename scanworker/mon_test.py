
from celery import Celery
from monitor import ScanWorkerActiveMarker


def main(app, freq=1.0):
	state = app.events.State()
	with app.connection() as connection:
		recv = app.events.Receiver(connection, handlers={'*': state.event})
		with ScanWorkerActiveMarker(state, freq=freq):
			recv.capture(limit=None, timeout=None)

if __name__ == '__main__':
	celery = Celery(broker='amqp://phagemasteruser:longmasterpassword@scanmaster/phage')
	main(celery)