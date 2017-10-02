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

from libs.slackbot import SlackBot
from libs import newsletter as nw

api = Flask(__name__)
if os.environ.get("SERVER_SECRET"):
	api.secret_key = os.environ.get("SERVER_SECRET")
else:
	print("No secret provided")


def loginrequired(func):
	@wraps(func)
	def core(*args, **kwargs):
		if "user" in session:
			user = json.loads(session.get("user"))
			kwargs["user"] = user
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
	bot = SlackBot()
	code = request.args.get("code")
	auth_response = bot.auth_call(code)
	if auth_response.get("ok"):
		user = {
			"user_id": auth_response.get("user").get("id"),
			"email": auth_response.get("user").get("email"),
			"name": auth_response.get("user").get("name"),
			"team": auth_response.get("team").get("id"),
			"access_token": auth_response.get("access_token")
		}

		session["user"] = json.dumps(user)
		return redirect(url_for("newsletter"))

	return json.dumps(auth_response), 200


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
	scope = "identity.basic, identity.team, identity.email, identity.avatar, channels:read, groups:read"
	return render_template("login.html", client_id=client_id, scope=scope)


@api.route("/auth/logout")
@loginrequired
def logout(user):
	if "user" in session:
		session.pop("user", None)
	return redirect(url_for("newsletter"))


@api.route("/newsletter")
@loginrequired
def newsletter(user):
	channels = nw.gettopics(user)
	return render_template("newsletter/index.html", user=user, channels=channels)

@api.route("/newsletter/<string:channel>")
@loginrequired
def keyword(channel, user):
	channels = nw.getnews(user, channel)
	return render_template("newsletter/news.html", user=user, channels=channels)


if __name__ == "__main__":
	api.run(host="0.0.0.0", debug=True)