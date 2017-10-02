from libs.database import DB

from slackclient import SlackClient

db = DB()

class Newsletter(object):
	def __init__(self, access_token):
		self.access_token = access_token

	def gettopics(self):
		try:
			channels = []

			client = SlackClient(self.access_token)
			response = client.api_call("channels.list")
			if response and response.get("ok"):
				for channel in response.get("channels"):
					channels.append({
						"id": channel.get("id"),
						"name": channel.get("name")
					})

			print(channels)

			return channels
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