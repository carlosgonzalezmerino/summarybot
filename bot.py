import os
import re
import time

import messages

import requests
from langdetect import detect
from bs4 import BeautifulSoup
from slackclient import SlackClient

API_ENDPOINT="http://api-atomo-news.herokuapp.com/summary"


class SummaryBot(object):
	def __init__(self):
		self.name = os.environ.get("SLACK_BOT_NAME")
		self.token = os.environ.get("SLACK_API_TOKEN")

		if self.token and self.name:
			self.client = SlackClient(self.token)

			response = self.client.api_call('users.list')
			if response.get("ok"):
				candidates = list(filter(lambda user: user.get("name") == self.name, response.get("members")))

				if len(candidates) != 1:
					raise Exception("Ambiguous bot name ;(")

				self.id = candidates[0].get("id")
		else:
			raise Exception("Token and name required")

	def listen(self):
		self.__messagelistener()

	def __messagelistener(self):
		if self.client.rtm_connect(with_team_state=False):
			while True:
				msgs = self.client.rtm_read()
				if len(msgs):
					self.__messagehandler(msgs[0])
		else:
			raise Exception("Connection Failed")

	def __messagehandler(self, msg):
		text = msg.get("text")
		response = {
			"channel": msg.get("channel"),
			"thread_ts": msg.get("ts")
		}

		if text and self.__itsforme(text):
			url = self.__detecturl(text)
			if url:
				content = self.__geturlcontent(url)
				if content:
					summary = self.__getsummary(content)
					if summary:
						response["text"] = "*{}*\n\n".format(content.get("title")) + "\n".join(summary)
						response.pop("thread_ts", None)
					else:
						response["text"] = messages.NO_SUMMARY
				else:
					response["text"] = messages.EXTERNAL_ERROR
			else:
				response["text"] = messages.NO_URL

			self.__sendmessage(response)
		return

	def __itsforme(self, text):
		mentionregex = re.compile(r"<@(?P<id>[A-Z0-9]+)>.+")
		catched = mentionregex.search(text)
		if catched:
			return bool(catched.group("id"))

	def __detecturl(self, text):
		urlmatcher = re.compile(r"<(?P<url>http[s]?\:\/\/[^\s]+)>")

		match = urlmatcher.search(text)
		if match:
			return match.group("url")

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

	def __sendmessage(self, msg):
		time.sleep(1)
		self.client.api_call("chat.postMessage", **msg)
		return

if __name__ == "__main__":
	bot = SummaryBot()
	bot.listen()