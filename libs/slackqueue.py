class SlackQueue(object):
	def __init__(self, buffer_size):
		self.size = buffer_size
		self.queue = []

	def check(self, event, filters):
		if not isinstance(event, dict) or not isinstance(filters, list):
			return False

		for filter in filters:
			if not filter in event.keys():
				return False

		return True

	def contains(self, event, filters):
		if not isinstance(event, dict) or not isinstance(filters, list):
			return -1

		to_check = []
		for key in event.keys():
			if key in filters:
				to_check.append(key)

		if len(to_check) != len(filters):
			return -1

		for enqueue in self.queue:
			checked = 0
			for filter in to_check:
				if enqueue[filter] == event[filter]:
					checked += 1

			if checked == len(to_check):
				return 1
		return 0

	def append(self, event):
		if not isinstance(event, dict):
			return False

		if len(self.queue) == self.size:
			del self.queue[0]

		self.queue.append(event)
		return True

	def remove(self, event):
		self.queue.remove(event)
		return True