from datetime import datetime
from datetime import timedelta
from libs.database import DB
from slackclient import SlackClient

db = DB()

class Newsletter(object):
	def __init__(self, access_token):
		self.access_token = access_token

	def __getchannels(self):
		channels = []

		client = SlackClient(self.access_token)
		response = client.api_call("channels.list")
		if response and response.get("ok"):
			for channel in response.get("channels"):
				channels.append({
					"id": channel.get("id"),
					"name": channel.get("name")
				})

		response = client.api_call("groups.list")
		if response and response.get("ok"):
			for group in response.get("groups"):
				channels.append({
					"id": group.get("id"),
					"name": group.get("name")
				})

		return channels or None

	def __getkeywords(self, channels):
		links = []
		for channel in channels:
			links += db.getAll("news", "channel_id", channel.get("id"))

		print(links)

		keywords = {}
		end = datetime.today() - timedelta(days=datetime.today().weekday())
		start = end - timedelta(days=7)
		for link in links:
			if end > link.get("date") >= start:
				link_keywords = link.get("keywords").split(",")

				for keyword in link_keywords:
					if keyword in keywords.keys():
						keywords[keyword].append(link)
					else:
						keywords[keyword] = [link]

		return keywords or None

	def gettopics(self):
		try:
			channels = self.__getchannels()
			print(channels)
			if channels:
				return self.__getkeywords(channels)
		except Exception as e:
			print(e)

		return None

	def getlinks(user, channel_id):
		try:
			news = db.getAll("news", "channel_id", channel_id)
			for new in news:
				new["keywords"] = new.get("keywords").split(",")

			return news
		except Exception as e:
			print(e)

		return None