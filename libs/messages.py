
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
			self.INTRO = "How do you do today? My name is *Reverte Bot* and despite yesterday I was long hours in my Greek library, I am at this forum today *to help you extract the best out of any article that might be published*."
			self.CONTENT_NOMENTION_MSG = "Being well aware that nobody invite me here, here you have my sapiency on the topic you have just share."
			self.CONTENT_MSG = "In these short lines, I neatly summarize the content from your link."
			self.CONTENT_ALREADY_SENT = "I am oblied to inform you that this hyperlink was previously posted by another user on {}. This turns this moment into a “Groundhog Day”. Despite this fact, here you have a selection of its best sentences:"
			self.NO_URL = "Dear user, your message must contain a link or you will regreat wasting my time whit this useless chit-chat."
			self.NO_CONTENT = "I am afraid I search in your link and there was not any content I could understand... It is clear that it is your fault."
			self.EXTERNAL_ERROR = "There seems to be a problem with the link you sent, I should complain in twitter..."
			self.NO_SUMMARY = "I must confess I was not able to summarize that link, I am seeing the decadence of my art... I am going back to twitter."
