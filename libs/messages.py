
class Messages(object):
	def __init__(self, lang):
		if lang == "spanish":
			self.INTRO = "¿Cómo se halla hoy Vuesa Merced? Me llamo *Reverte Bot* y aunque ayer anduve un rato por mi biblioteca en la parte ocupada por clasicos griegos, hoy transito hacia este foro para *ayudar a extraer lo mejor de las noticias o articulos que aquí se viertan*."
			self.CONTENT_NOMENTION_MSG = "Sabiendo que nadie me ha dado vela en este entierro, le otorgo mi sabiduría sobre lo que acaba de exponer."
			self.CONTENT_MSG = "En estas líneas resumo de forma escueta el contenido de su enlace."
			self.CONTENT_ALREADY_SENT = "Me veo en la obligación de informarle de que este hipervínculo ya fue compartido por otro usuario el {}. Esta situación lo convierte en un claro “gol de señor”. A pesar de ello vea a continuación una selección de las mejores frases de dicho texto:"
			self.NO_URL = "Muy señor mío, el mensaje debe incluir un enlace o  pagará caro ocupar mi tiempo de esta manera."
			self.NO_CONTENT = "Vaya, me he pasado por el enlace que me ha mandado, pero no he encontrado nada... Me lo paso por la bisectriz del ángulo principal."
			self.EXTERNAL_ERROR = "Parece que el enlace que ha mandado no responde, voy a quejarme en twitter..."
			self.NO_SUMMARY = "No he sido capaz de resumir ese enlace, siento que mi arte está en decadencia... vuelvo a twitter."
		elif lang == "english":
			self.INTRO = "¿Cómo se halla hoy Vuesa Merced? Me llamo *Reverte Bot* y aunque ayer anduve un rato por mi biblioteca en la parte ocupada por clasicos griegos, hoy transito hacia este foro para *ayudar a extraer lo mejor de las noticias o articulos que aquí se viertan*."
			self.CONTENT_NOMENTION_MSG = "Sabiendo que nadie me ha dado vela en este entierro, le otorgo mi sabiduría sobre lo que acaba de exponer."
			self.CONTENT_MSG = "En estas líneas resumo de forma escueta el contenido de su enlace."
			self.CONTENT_ALREADY_SENT = "Me veo en la obligación de informarle de que este hipervínculo ya fue compartido por otro usuario el {}. Esta situación lo convierte en un claro “gol de señor”. A pesar de ello vea a continuación una selección de las mejores frases de dicho texto:"
			self.NO_URL = "Muy señor mío, el mensaje debe incluir un enlace o  pagará caro ocupar mi tiempo de esta manera."
			self.NO_CONTENT = "Vaya, me he pasado por el enlace que me ha mandado, pero no he encontrado nada... Me lo paso por la bisectriz del ángulo principal."
			self.EXTERNAL_ERROR = "Parece que el enlace que ha mandado no responde, voy a quejarme en twitter..."
			self.NO_SUMMARY = "No he sido capaz de resumir ese enlace, siento que mi arte está en decadencia... vuelvo a twitter."
