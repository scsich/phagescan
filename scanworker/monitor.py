
from virusscan.models import get_active_q_dict_from_cache
from virusscan.models import ScannerType
from celery.events.snapshot import Polaroid


class ScanWorkerActiveMarker(Polaroid):
	last_alive_workers = -1

	def on_shutter(self, state):
		if not state.event_count:
			# No new events since last snapshot.
			return

		current_worker_count = len(state.alive_workers())

		if self.last_alive_workers != current_worker_count:
			active_queues = get_active_q_dict_from_cache(inspect=self.app.control.inspect())
			ScannerType.objects.set_active_by_q_dict(active_queues)
			self.last_alive_workers = current_worker_count
