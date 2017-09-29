import json
from urllib.parse import quote_plus

from flask import Flask
from flask import url_for
from flask import request
from flask import session
from flask import redirect
from flask import make_response
from flask import render_template

from libs.slackbot import SlackBot

api = Flask(__name__)


@api.route("/")
def index():
	bot = SlackBot()
	client_id = bot.oauth.get("client_id")
	scope = bot.oauth.get("scope")
	return render_template("index.html", client_id=client_id, scope=scope)


@api.route("/thanks")
def thanks():
	bot = SlackBot()
	code = request.args.get("code")
	if code:
		bot.auth(code)
		return render_template("thanks.html")
	else:
		return render_template("error.html")


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


@api.route("/login")
def login():
	bot = SlackBot()
	code = request.args.get("code")
	if not code:
		client_id = bot.oauth.get("client_id")
		scope = "identity.basic, identity.team, identity.email"

		url = quote_plus("https://bot.myshortreport.com/login")
		return render_template("login.html", client_id=client_id, scope=scope, redirect=url)
	else:
		auth_response = bot.auth_call(code)
		print(auth_response)
	return "Ok", 200


@api.route("/newsletter")
def newsletter():
	code = request.args.get("code")
	token = session.get("token")
	if token:
		return render_template("newsletter.html")

	return redirect(url_for('login'))


if __name__ == "__main__":
	api.run(host="0.0.0.0", debug=True)