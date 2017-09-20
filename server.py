import json
from flask import Flask
from flask import request
from flask import make_response
from flask import render_template

app = Flask(__name__)


class Server(object):
	def __init__(self, bot):
		self.bot = bot
		self.app = app

		self.app.add_url_rule("/listen", "listen", self.listen)
		self.app.add_url_rule("/install", "install", self.install)
		self.app.add_url_rule("/thanks", "thanks", self.thanks)

	def run(self):
		self.app.run(debug=True)

	def listen(self):
		slack_event = json.loads(request.data)

		if "challenge" in slack_event:
			return make_response(slack_event.get("challenge"), 200, {"content_type": "application/json"})

		if self.bot.verification == slack_event.get("token"):
			event = slack_event.get("event")
			if event and event.get("type") == "message":
				team_id = slack_event.get("team_id")
				self.bot.listen(team_id)
		else:
			return make_response("Invalid Slack verification code", 403)


	def install(self):
		client_id = self.bot.oauth.get("client_id")
		scope = self.bot.oauth.get("scope")
		return render_template("install.html", client_id=client_id, scope=scope)

	def thanks(self):
		code = request.args.get("code")
		if code:
			self.bot.auth(code)
			return render_template("thanks.html")
		else:
			return render_template("error.html")