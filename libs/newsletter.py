import re
from math import ceil
from datetime import datetime
from datetime import timedelta
from slackclient import SlackClient
from libs.database import DB

WORDSPERMIN=220


class Newsletter(object):
	def __init__(self, access_token):
		self.access_token = access_token
		self.db = DB()

	def __readtime(self, text):
		splitter = re.compile("\s")
		words = splitter.split(text)
		return ceil(len(words)/WORDSPERMIN)

	def __getchannel(self, id):
		channels = self.__getchannels()

		if channels:
			for channel in channels:
				if channel.get("id") == id:
					return channel

		return None

	def __getauthor(self, id):
		if id:
			client = SlackClient(self.access_token)

			response = client.api_call("users.info", user=id)
			if response.get("ok"):
				return response.get("user")

			return None

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

	def __formatlink(self, new):
		keywords = new.get("keywords")
		if keywords:
			tags = keywords.split(",")
			if tags:
				channel = self.__getchannel(new.get("channel_id"))
				author = self.__getauthor(new.get("user_id"))
				del new["channel_id"]
				del new["user_id"]

				if channel:
					channel = {
						"id": channel.get("id"),
						"name": channel.get("name")
					}

				if author:
					profile = author.get("profile")
					if profile:
						author = {
							"id": author.get("id"),
							"name": profile.get("real_name") or author.get("name"),
							"avatar": profile.get("image_72")
						}
					else:
						author = {
							"id": author.get("id"),
							"name": author.get("name"),
							"avatar": None
						}

				new["channel"] = channel
				new["author"] = author
				new["keywords"] = tags
				new["readtime"] = self.__readtime(new.get("summary"))
				new["summary"] = new.get("summary").split("\n\n")
		return new

	def __getkeywords(self, channels):
		links = []
		for channel in channels:
			links += self.db.getAll("news", "channel_id", channel.get("id"))

		keywords = []
		for link in links:
			all_keywords = link.get("keywords").split(",")
			for keyword in all_keywords:
				if not keyword in keywords:
					keywords.append(keyword)

		return keywords or None

	def gettopics(self):
		try:
			channels = self.__getchannels()
			if bool(channels):
				return self.__getkeywords(channels)
		except Exception as e:
			print(e)

		return None

	def getrecents(self):
		end = datetime.today() - timedelta(days=datetime.today().weekday())
		start = end - timedelta(days=7)

		try:
			channels = self.__getchannels()
			channels_ids = [channel.get("id") for channel in channels]

			links = []
			news = self.db.getByDate("news", "date", start, end)
			for new in news:
				if new.get("channel_id") in channels_ids:
					link = self.__formatlink(new)
					links.append(link)

			return links
		except Exception as e:
			print(e)

		return None

	def getlinks(self, topic):
		try:
			links = []
			news = self.db.getAll("news")
			for new in news:
				keywords = new.get("keywords")
				if keywords:
					tags = keywords.split(",")
					if topic in tags:
						new["keywords"] = tags
						new["summary"] = new.get("summary").split("\n\n")
						links.append(new)

			return links or None
		except Exception as e:
			print(e)

		return None