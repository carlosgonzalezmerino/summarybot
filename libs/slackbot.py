import os
import re

from datetime import datetime

import requests
from bs4 import BeautifulSoup
from langdetect import detect
from slackclient import SlackClient

from libs import messages
from libs.database import DB

API_ENDPOINT="http://api-atomo-news.herokuapp.com/summary"


class SlackBot(object):
	def __init__(self):
		self.db = DB()

		self.id = None
		self.name = os.environ.get("SLACK_BOT_NAME")
		self.verification = os.environ.get("SLACK_VERIFICATION_TOKEN")
		self.oauth = {
			"client_id": os.environ.get("SLACK_CLIENT_ID"),
			"client_secret": os.environ.get("SLACK_CLIENT_SECRET"),
			"scope": "bot,channels:history,groups:history,im:history"
		}

		if self.name and self.verification and self.oauth.get("client_id") and self.oauth.get("client_secret"):
			self.client = SlackClient("")
		else:
			raise Exception("Token and name required")

	def __getmyinfo(self):
		response = self.client.api_call('users.list')
		if response.get("ok"):
			self.users = response.get("members")
			candidate = self.__findmember(name=self.name)

			if not candidate:
				raise Exception("Bot name not found ;(")
			elif isinstance(candidate, list):
				raise Exception("Ambiguous bot name ;(")
			else:
				self.id = candidate.get("id")
				print("BOT ID: %s" % self.id)
		else:
			print(response)
			raise Exception("Error getting user list info")

	def __itsforme(self, event):
		text = event.get("text")
		if text:
			mentionregex = re.compile(r"<@(?P<id>[A-Z0-9]+)>")
			catched = mentionregex.search(text)
			if catched:
				return bool(catched.group("id") == self.id)
		return False

	def __findmember(self, id=None, name=None):
		results = []
		if id:
			results = list(filter(lambda user: user.get("id") == id, self.users))
		elif name:
			results = list(filter(lambda user: user.get("name") == name, self.users))
			if not results:
				results = list(filter(lambda user: user.get("real_name") == name, self.users))

		if results:
			if len(results) == 1:
				return results[0]
			else:
				return results
		return None

	def __eventeanswered(self, user, channel, url):
		try:
			exists = self.db.get("news", {
				"url": url,
				"user_id": user,
				"channel_id": channel
			})

			return bool(exists)
		except Exception as e:
			print(e)

		return False

	def __parseurl(self, text):
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

			body = response.text.encode('latin1')
			soup = BeautifulSoup(body, 'lxml')
			if "bbva.com" not in url:
				article = self.__parsecontent(soup)
			else:
				article = soup.find("section", class_="article-body")

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

		return {
			"title": None,
			"text": None
		}

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
			return data.get("highlights"), data.get("keywords")
		except Exception as e:
			print(e)

		return None, None

	def __parsetitle(self, raw):
		title = raw
		patterns = [" - ", " | "]

		for pattern in patterns:
			if pattern in raw:
				title = raw.split(pattern)[0]
				break

		return "{}".format(title)

	def __parsecontent(self, soup):
		prop = re.compile("articleBody", re.IGNORECASE)
		tag = re.compile("article|article-.+", re.IGNORECASE)
		id = re.compile("(content|post).*", re.IGNORECASE)
		_class = re.compile("(post|article|blog|article-*).*", re.IGNORECASE)

		return soup.find(itemprop=prop) or soup.find(class_=_class) or soup.find(tag) or soup.find(id=id)


	def __parseattachments(self, raw_title, summary, url):
		data = {
			"color": "good",
			"title": self.__parsetitle(raw_title),
			"title_link": url,
			"text": "\n\n".join(summary)
		}

		return [data]

	def __save(self, article):
		title = article.get("title")
		if title:
			try:
				exists = self.db.count("news", "title", title)
				if not exists:
					self.db.add("news", article)
					return True
			except Exception as e:
				print(e)

		return False

	def __sendresponse(self, response):
		if response:
			try:
				self.client.api_call("chat.postMessage", **response)
			except Exception as e:
				print(e)
		return

	def auth(self, code, uri=None):
		auth_response = self.auth_call(code, uri)

		if auth_response:
			team_id = auth_response.get("team_id")
			if team_id:
				bot = auth_response.get("bot")
				if bot:
					try:
						count = self.db.count("auths", "team_id", team_id)
						if count:
							self.db.update("auths", {"bot_token": bot.get("bot_access_token")}, "team_id", team_id)
						else:
							self.db.add("auths", {"team_id": team_id, "bot_token": bot.get("bot_access_token")})
						return True
					except Exception as e:
						print(e)

		return False

	def auth_call(self, code, uri=None):
		try:
			if uri:
				auth_response = self.client.api_call(
					"oauth.access",
					client_id=self.oauth["client_id"],
					client_secret=self.oauth["client_secret"],
					redirect_uri=uri,
					code=code
				)
			else:
				auth_response = self.client.api_call(
					"oauth.access",
					client_id=self.oauth["client_id"],
					client_secret=self.oauth["client_secret"],
					code=code
				)
			if auth_response.get("ok"):
				return auth_response
			else:
				raise(auth_response.get("error"))
		except Exception as e:
			print(e)

		return None

	def connect(self, team_id):
		try:
			authorized = self.db.get("auths", {"team_id": team_id})

			self.client = SlackClient(authorized.get("bot_token"))
			self.__getmyinfo()
		except Exception as e:
			print(e)
		return

	def event_handler(self, event, workspace):
		channel = event.get("channel")
		user = event.get("user")
		text = event.get("text")
		ts = event.get("ts")
		url = self.__parseurl(text)
		response = {"channel": channel}

		exists = self.__eventeanswered(user, channel, url)
		if not exists:
			itsforme = self.__itsforme(event)
			iamnew = itsforme and event.get("subtype") == "channel_join"
			itsbot = event.get("subtype") == "bot_message"
			nosubtype = event.get("subtype") is None

			if not itsbot:
				if iamnew:
					response["text"] = messages.INTRO
				elif nosubtype and url and itsforme:
					content = self.__geturlcontent(url)
					if content:
						title = content.get("title")
						summary, keywords = self.__getsummary(content)
						if summary and keywords:
							response["text"] = messages.CONTENT_MSG
							response["attachments"] = self.__parseattachments(title, summary, url)
							try:
								article = {
									"title": title,
									"summary": "\n\n".join(summary),
									"keywords": ",".join(keywords),
									"url": url,
									"user_id": user,
									"channel_id": channel,
									"workspace": workspace,
									"date": datetime.now()
								}
								self.__save(article)
							except Exception as e:
								print(e)
						else:
							response["text"] = messages.NO_SUMMARY
							response["thread_ts"] = ts
					else:
						response["text"] = messages.EXTERNAL_ERROR
				elif nosubtype and url and not itsforme:
					content = self.__geturlcontent(url)
					if content:
						title = content.get("title")
						summary, keywords = self.__getsummary(content)
						if summary and keywords:
							response["text"] = messages.CONTENT_MSG
							response["thread_ts"] = ts
							response["attachments"] = self.__parseattachments(title, summary, url)

							try:
								article = {
									"title": title,
									"summary": "\n\n".join(summary),
									"keywords": ",".join(keywords),
									"url": url,
									"user_id": user,
									"channel_id": channel,
									"workspace": workspace,
									"date": datetime.now()
								}
								self.__save(article)
							except Exception as e:
								print(e)
				elif nosubtype and itsforme and not url:
					response["text"] = messages.NO_URL
					response["thread_ts"] = ts
				else:
					response = None
				self.__sendresponse(response)
		return