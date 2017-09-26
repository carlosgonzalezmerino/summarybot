import os
import re
import sys
import time
import logging

import requests
from langdetect import detect
from bs4 import BeautifulSoup
from slackclient import SlackClient

import messages

API_ENDPOINT="http://api-atomo-news.herokuapp.com/summary"


class SummaryBot(object):
	def __init__(self):
		self.name = os.environ.get("SLACK_BOT_NAME")
		self.token = os.environ.get("SLACK_API_TOKEN")
		self.logger = logging.getLogger(__name__)
		self.users = []

		if self.token and self.name:
			self.client = SlackClient(self.token)

			response = self.client.api_call('users.list')
			if response.get("ok"):
				self.users = response.get("members")
				candidate = self.__findmember(name=self.name)

				if not candidate:
					raise Exception("Bot name not found ;(")
				elif isinstance(candidate, list):
					raise Exception("Ambiguous bot name ;(")

				self.id = candidate.get("id")

				print("Bot ID:" + self.id)
			else:
				raise Exception("Error getting user list info")
		else:
			raise Exception("Token and name required")

	def listen(self):
		if self.client.rtm_connect(with_team_state=False):
			print("Listening...")
			while True:
				msgs = self.client.rtm_read()
				if len(msgs):
					self.__messagehandler(msgs[0])
		else:
			raise Exception("Connection Failed")

	def __messagehandler(self, msg):
		if msg.get("type") == "message" and msg.get("subtype") != "channel_join":
			thread = not self.__itsforme(msg)
			response = self.__parserequest(msg, thread)
			if response:
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

	def __findmember(self, id=None, name=None):
		results = []
		if id:
			results = list(filter(lambda user: user.get("id") == id, self.users))
		elif name:
			results = list(filter(lambda user: user.get("name") == name, self.users))

		if results:
			if len(results) == 1:
				return results[0]
			else:
				return results
		return None

	def __parserequest(self, msg, thread=None):
		author = None
		if msg.get("user"):
			author = self.__findmember(id=msg.get("user"))
			if author.get("id") == self.id:
				author = None

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
					if author:
						sys.stdout.write("[Summary generated] Link: {url} User: {user}\n".format(url=url, user=author.get("name")))

					response["attachments"] = self.__parsecontent(title, summary, url)
					if thread:
						response["text"] = messages.CONTENT_NOMENTION_MSG
					else:
						response["text"] = messages.CONTENT_MSG
						response.pop("thread_ts", None)
				else:
					response["text"] = messages.NO_SUMMARY
			else:
				response["text"] = messages.EXTERNAL_ERROR
		elif not thread:
			response["text"] = messages.NO_URL
		else:
			return None

		return response

	def __parseurl(self, msg):
		text = msg.get("text")
		if text:
			urlmatcher = re.compile(r"<(?P<url>http[s]?\:\/\/[^\s]+)>")

			match = urlmatcher.search(text)
			if match:
				return match.group("url")
		return False

	def __getarticle(self, soup):
		prop = re.compile("articleBody")
		tag = re.compile("article|article-.+")
		id = re.compile("(content|post).*")
		_class = re.compile("(post|article).*")

		return soup.find(itemprop=prop) or soup.find(tag) or soup.find(id=id) or soup.find(_class=_class)

	def __geturlcontent(self, url):
		try:
			response = requests.get(url)
			response.raise_for_status()

			body = response.text
			soup = BeautifulSoup(body, 'lxml')
			article = self.__getarticle(soup)
			if article:
				title = soup.title.getText()
				paragraphs = []
				for p in article.find_all('p', recursive=True):
					paragraphs.append(p.getText())

				return {
					"title": title,
					"text": "\n".join(paragraphs),
				}
			return None
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

if __name__ == "__main__":
	bot = SummaryBot()
	bot.listen()