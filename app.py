from bot import SummaryBot
from server import Server


def main():
	bot = SummaryBot()

	server = Server(bot)
	server.run()


if __name__ == "__main__":
	main()
