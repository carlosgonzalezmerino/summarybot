from libs.database import DB

from slackclient import SlackClient

db = DB()


def gettopics(user):
	try:
		channels = []
		auth = db.get("auths", {"team_id": user.get("team")})
		client = SlackClient(auth.get("bot_token"))

		all_channels = client.api_call("")

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

def revoketoken(user):
	try:
		client = SlackClient(user.get("access_token"))
		client.api_call("auth.revoke")
	except Exception as e:
		print(e)
		return False
	return True