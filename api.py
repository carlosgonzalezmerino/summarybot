import os
import json

from functools import wraps
from urllib.parse import quote_plus

from flask import Flask
from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import make_response
from flask import render_template

from libs.auth import Auth
from libs.slackbot import SlackBot
from libs.newsletter import Newsletter

api = Flask(__name__)
if os.environ.get("SERVER_SECRET"):
	api.secret_key = os.environ.get("SERVER_SECRET")
else:
	print("No secret provided")


def loginrequired(func):
	@wraps(func)
	def core(*args, **kwargs):
		if "data" in session:
			data = json.loads(session.get("data"))
			kwargs["data"] = data
			return func(*args, **kwargs)
		else:
			return redirect(url_for("login"))

	return core


@api.route("/")
def index():
	bot = SlackBot()
	client_id = bot.oauth.get("client_id")
	scope = bot.oauth.get("scope")
	url = quote_plus("https://bot.myshortreport.com/auth/bot")
	return render_template("index.html", client_id=client_id, scope=scope, redirect=url)


@api.route("/listen", methods=["GET","POST"])
def listen():
	slack_event = json.loads(request.data.decode("utf-8"))

	if "challenge" in slack_event:
		return make_response(slack_event.get("challenge"), 200, {"content_type": "application/json"})

	bot = SlackBot()
	if bot.verification == slack_event.get("token"):
		event = slack_event.get("event")
		if event and event.get("type") == "message":
			team_id = slack_event.get("team_id")
			bot.connect(team_id)
			from pprint import pprint
			pprint(event, indent=4)

			bot.event_handler(event, team_id)
		return "Ok", 200
	else:
		return make_response("Invalid Slack verification code", 403)


@api.route("/auth")
def auth():
	auth = Auth()
	code = request.args.get("code")
	if code and auth.request(code):
		session["data"] = json.dumps(auth.data)
		return redirect(url_for("newsletter"))

	return "Forbidden", 403


@api.route("/auth/bot")
def thanks():
	bot = SlackBot()
	code = request.args.get("code")
	if code:
		bot.auth(code)
		return render_template("thanks.html")
	else:
		return render_template("error.html")


@api.route("/auth/login")
def login():
	bot = SlackBot()
	client_id = bot.oauth.get("client_id")
	scope = "users.profile:read, groups:read, channels:read"
	return render_template("login.html", client_id=client_id, scope=scope)


@api.route("/auth/logout")
@loginrequired
def logout(data=None):
	auth = Auth()
	auth.revoke()
	if "user" in session:
		session.pop("data", None)
	return redirect(url_for("newsletter"))


@api.route("/newsletter")
@loginrequired
def newsletter(data):
	nw = Newsletter(data.get("access_token"))
	topics = nw.gettopics()
	print(topics)
	return render_template("newsletter/index.html", data=data, topics=topics)

@api.route("/newsletter/<string:topic>")
@loginrequired
def keyword(data, topic):
	nw = Newsletter(data.get("access_token"))
	links = nw.getlinks(topic)
	return render_template("newsletter/news.html", data=data, links=links)


if __name__ == "__main__":
	api.run(host="0.0.0.0", debug=True)