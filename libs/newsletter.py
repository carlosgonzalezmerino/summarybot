from libs.database import DB

db = DB()

def getLinks(channel_id):
	try:
		news = db.getAll("news", "channel_id", channel_id)
		for new in news:
			new["keywords"] = new.get("keywords").split(",")

		return news
	except Exception as e:
		print(e)

	return None