import os

from slackclient import SlackClient

from libs.database import DB


class Auth(object):
	def __init__(self):
		self.db = DB()
		self.client = SlackClient("")
		self.verification = os.environ.get("SLACK_VERIFICATION_TOKEN")
		self.data = None
		self.oauth = {
			"client_id": os.environ.get("SLACK_CLIENT_ID"),
			"client_secret": os.environ.get("SLACK_CLIENT_SECRET")
		}

	def request(self, code):
		try:
			res = self.client.api_call(
				"oauth.access",
				client_id=self.oauth["client_id"],
				client_secret=self.oauth["client_secret"],
				code=code
			)
			if res and res.get("ok"):
				self.data = {
					"access_token": res.get("access_token"),
					"user_id": res.get("user_id"),
					"team_id": res.get("team_id")
				}
				self.client = SlackClient(self.data.get("access_token"))
				return True
		except Exception as e:
			print("Error getting authorization with code: %s" % code)
			print(e)

		return False

	def revoke(self):
		try:
			self.client.api_call("auth.revoke")
			return True
		except Exception as e:
			print(e)
		return False
