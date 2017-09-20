import os
import re
import time

import requests
from langdetect import detect
from bs4 import BeautifulSoup
from slackclient import SlackClient

import messages
from database import DB

API_ENDPOINT="http://api-atomo-news.herokuapp.com/summary"



class SummaryBot(object):
	def __init__(self):
		self.name = os.environ.get("SLACK_BOT_NAME")
		self.verification = os.environ.get("SLACK_VERIFICATION_TOKEN")
		self.oauth = {
			"client_id": os.environ.get("SLACK_CLIENT_ID"),
			"client_secret": os.environ.get("SLACK_CLIENT_SECRET"),
			"scope": "bot"
		}

		self.authorized = []
		self.db = DB()

		if self.name and self.verification and self.oauth.get("client_id") and self.oauth.get("client_secret"):
			self.client = SlackClient("")

			response = self.client.api_call('users.list')
			if response.get("ok"):
				candidates = list(filter(lambda user: user.get("name") == self.name, response.get("members")))

				if len(candidates) != 1:
					raise Exception("Ambiguous bot name ;(")

				self.id = candidates[0].get("id")
		else:
			raise Exception("Token and name required")

	def auth(self, code):
		auth_response = self.client.api_call(
			"oauth.access",
			client_id=self.oauth["client_id"],
			client_secret=self.oauth["client_secret"],
			code=code
		)

		team_id = auth_response.get("team_id")
		if team_id:
			bot = auth_response.get("bot")
			if bot:
				try:
					data = {"team_id": team_id,"bot_token": bot.get("bot_access_token")}
					self.db.add("auths", data)
					return True
				except Exception as e:
					print(e)
		return False

	def listen(self, team_id):
		try:
			authorized = self.db.get("auths", {"team_id": team_id})
		except Exception as e:
			print(e)
			return

		self.client = SlackClient(authorized.get("bot_token"))
		if self.client.rtm_connect():
			while True:
				msgs = self.client.rtm_read()
				if len(msgs):
					self.__messagehandler(msgs[0])
		else:
			raise Exception("Connection Failed")

	def __messagehandler(self, msg):
		if self.__itsforme(msg):
			response = self.__parserequest(msg)
			self.__sendmessage(response)

		return

	def __itsforme(self, msg):
		text = msg.get("text")
		if text:
			mentionregex = re.compile(r"<@(?P<id>[A-Z0-9]+)>.+")
			catched = mentionregex.search(text)
			if catched:
				return bool(catched.group("id"))
		return False

	def __parserequest(self, msg):
		response = {
			"channel": msg.get("channel"),
			"thread_ts": msg.get("ts")
		}

		url = self.__parseurl(msg)
		if url:
			content = self.__geturlcontent(url)
			title = content.get("title")
			if content:
				summary = self.__getsummary(content)
				if summary:
					response["text"] = messages.CONTENT_MSG
					response["attachments"] = self.__parsecontent(title, summary, url)
					response.pop("thread_ts", None)
				else:
					response["text"] = messages.NO_SUMMARY
			else:
				response["text"] = messages.EXTERNAL_ERROR
		else:
			response["text"] = messages.NO_URL

		return response

	def __parseurl(self, msg):
		text = msg.get("text")
		if text:
			urlmatcher = re.compile(r"<(?P<url>http[s]?\:\/\/[^\s]+)>")

			match = urlmatcher.search(text)
			if match:
				return match.group("url")
		return False

	def __geturlcontent(self, url):
		try:
			response = requests.get(url)
			response.raise_for_status()

			body = response.text
			soup = BeautifulSoup(body, 'lxml')
			article = soup.find('article')

			title = soup.title.getText()
			paragraphs = []
			for p in article.find_all('p', recursive=True):
				paragraphs.append(p.getText())

			return {
				"title": title,
				"text": "\n".join(paragraphs),
			}
		except Exception as e:
			print(e)

		return None

	def __getsummary(self, content):
		try:
			req = {
				"lang": detect(content.get("text")),
				"input": content.get("text"),
				"count": 4
			}

			response = requests.post(API_ENDPOINT, data=req)
			response.raise_for_status()

			data = response.json()
			return data.get("highlights")
		except Exception as e:
			print(e)

		return None

	def __parsetitle(self, raw):
		title = raw
		patterns = [" - ", " | "]

		for pattern in patterns:
			if pattern in raw:
				title = raw.split(pattern)[0]
				break

		return "{}".format(title)

	def __parsecontent(self, raw_title, summary, url):
		data = {
			"color": "good",
			"title": self.__parsetitle(raw_title),
			"title_link": url,
			"text": "\n\n".join(summary)
		}

		return [data]


	def __sendmessage(self, msg):
		try:
			time.sleep(1)
			self.client.api_call("chat.postMessage", **msg)
		except Exception as e:
			print(e)
		return