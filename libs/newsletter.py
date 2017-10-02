from libs.database import DB

from slackclient import SlackClient

db = DB()


def gettopics(user):
	try:
		channels = []
		client = SlackClient(user.get("access_token"))

		response = client.api_call("groups.list", token=user.get("access_token"))
		if response.get("ok"):
			for c in response.get("channels"):
				channels.append({
					"id": c.get("id"),
					"name": c.get("name")
				})

		response = client.api_call("channels.list", token=user.get("access_token"))
		if response.get("ok"):
			channels = []
			for c in response.get("channels"):
				channels.append({
					"id": c.get("id"),
					"name": c.get("name")
				})

		news = []
		for channel in channels:
			news += db.getAll("news", "channel_id", channel.get("id"))

		print(news)

		keywords = []
		for new in news:
			temps = new.get("keywords").split(",")
			for k in temps:
				if k not in keywords:
					keywords.append(k)

		print(keywords)
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