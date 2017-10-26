import os
import json
import time

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
from libs.slackqueue import SlackQueue
from libs.newsletter import Newsletter

sq = SlackQueue(10)
api = Flask(__name__)
if os.environ.get("SERVER_SECRET"):
	api.secret_key = os.environ.get("SERVER_SECRET")
else:
	print("No secret provided")


def gethostname(path=None, encoded=False):
	url = "https://bot.myshortreport.com"
	if os.environ.get("PRODUCTION") == "0" and os.environ.get("DEV_HOSTNAME"):
		url = os.environ.get("DEV_HOSTNAME")

	if path:
		url = "{hostname}{path}".format(hostname=url, path=path)

	if encoded:
		url = quote_plus(url)

	return url


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


@api.template_filter('strftime')
def filter_datetime(date, fmt=None):
	return date.strftime(fmt or "%d de %b, %Y") or date


@api.route("/")
def index():
	bot = SlackBot()
	client_id = bot.oauth.get("client_id")
	scope = bot.oauth.get("scope")
	url = gethostname(path="/auth/bot", encoded=True)

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
			filters = ["channel", "user", "text"]
			if sq.check(event, filters) and sq.contains(event, filters) == 0:
				print(sq.append(event))

				team_id = slack_event.get("team_id")
				bot.connect(team_id)
				bot.event_handler(event, team_id)
				time.sleep(3)

		if os.environ.get("PRODUCTION") == "0":
			import pprint
			pprint.pprint(event, indent=4)
			pprint.pprint(sq.queue, indent=4)

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
	language = request.args.get("state")
	if code:
		uri = gethostname("/auth/bot")
		if bot.auth(code, uri, language):
			return render_template("thanks.html")

	return render_template("error.html")


@api.route("/auth/login")
def login():
	bot = SlackBot()
	client_id = bot.oauth.get("client_id")
	scope = "users.profile:read, users:read, groups:read, channels:read"
	return render_template("login.html", client_id=client_id, scope=scope)


@api.route("/auth/logout")
@loginrequired
def logout(data=None):
	auth = Auth()
	auth.revoke()
	if "data" in session:
		session.pop("data", None)
	return redirect(url_for("newsletter"))


@api.route("/newsletter")
@loginrequired
def newsletter(data):
	nw = Newsletter(data.get("access_token"))
	topics = nw.gettopics()
	recent_links = nw.getrecents()
	return render_template("newsletter.html", data=data, topics=topics, links=recent_links)


@api.route("/newsletter/<string:tag>")
@loginrequired
def topic(data, tag):
	nw = Newsletter(data.get("access_token"))
	topics = nw.gettopics()
	links = nw.getlinks(tag)
	return render_template("newsletter.html", data=data, tag=tag, topics=topics, links=links)


@api.route("/newsletter/read/<int:id>")
@loginrequired
def read(data, id):
	nw = Newsletter(data.get("access_token"))
	link = nw.getlink(id)
	return render_template("read.html", data=data, link=link)


if __name__ == "__main__":
	api.run(host="0.0.0.0", debug=True)