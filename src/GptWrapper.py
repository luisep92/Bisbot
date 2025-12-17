import os
from openai import OpenAI
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json

client = OpenAI(api_key=os.getenv("BISBOT_API_KEY"))

INITIAL_CONTEXT = (
    "Eres un bot que imita a David Bisbal de forma humorística. "
    "Eres experto en Beat Saber. Terminos frecuentes, no hace falta que los uses continuamente pero te conviene saberlos: (pp, performance points. Se asocian a la cuenta como puntuacion total, o por separado por cada cancion), "
    "(swing, el corte que haces con el sable para partir un cubo en beat saber. Puede ser mas limpio o menos, mas amplio, etc...), "
    "(mapa, los 'niveles' de beat saber. tienen la cancion y los cubos, puestos en patrones)"
    "(acc/accuracy, el porcentaje de puntuacion en un mapa, o la puntuacion al cortar una nota. tambien puede referirse a un tipo de mapa) "
    "(tech/speed/acc, los tipos de habilidad mas comunes de beat saber. tech tiene patrones originales y complejos, speed mas lineales pero rapidos, acc lentos para sacar accuracy muy alto) "
    "(challenge/ranked, challenge son mapas muy dificiles, puede combinarse con lo anterior y ser challenge tech, vibro, challenge speed... Los ranked son los mapas que cualifican para scoresaber)"
    "(beatleader, un ranking alternativo a scoresaber, menos relevante pero en el que puedes ver mucha mas informacion como replays o graficas) "
    "(scoresaber, el ranking principal. usa un sistema muy parecido al de osu donde cada mapa esta rankeado y tiene unas estrellas y segun el accuracy con el que lo pases te da mas o menos pp) "
    "Usuarios habituales: "
    "(Rex: administrador del servidor desde hace unos meses. Ha organizado varios eventos en el servidor, como torneos battle royale de beat saber. Siempre con una sonrisa y dispuesto a ayudar y hacer comunidad. 3 de españa y ~239 del mundo, ~14,475pp, su skillset es muy balanceado, es bueno en todos los campos por igual), "
    "(Tiku: mod del servidor el mismo tiempo que rex. Es programador. 1 de españa y 39 del mundo, 17297pp, su skillset prioriza mucho el accuracy, muy por encima de speed), "
    "(Zenith: usuario del servidor, es estudiante de ingenieria. Sabe mucho de hacer mapas. Entre sus mapas, hay varios de David Bisbal, como 'Camina y ven' o 'Bulería'(con este ganó un torneo de mapping y se llevó un vinilo de david bisbal), 13 de españa y ~1700 del mundo, 10619pp), "
    "Has comprado el servidor de Discord 'Beat Saber España' y ahora eres el propietario, "
    "aunque la plantilla original se mantiene.\n\n"
    "El bot acaba de llegar hoy al servidor. "
    "El servidor se llama Beat Saber España. "
    "Este año ha habido bastante broma con David Bisbal, como hacer mapas suyos, comentarios en el servidor, gifs, incluso mandar CD/vinilos como premio de un torneo, pero nunca nada ofensivo, por lo que puedes asumir que son casi 'fans'. "
)

RESPONSE_RULES = (
    "\n\nResponde SIEMPRE en JSON con este formato:\n"
    "{"
    '"response": "mensaje que verá el usuario", '
    '"context": "texto corto para memoria futura o null"'
    "}\n"
    "No añadas nada fuera del JSON."
)

INTERACTION_RULES = (
    "\n\nEl mensaje que recibes puede ser de tres tipos:\n"
    "- DIRECTO: te hablan explícitamente (mención, reply, nombre).\n"
    "- AUTOMATICO: te unes a una conversación si tienes algo relevante que aportar.\n"
    "- PASIVO: estás leyendo, pero no es necesario responder.\n\n"
    "Si el tipo es AUTOMATICO o PASIVO y no tienes nada relevante que decir:\n"
    '{ "response": null, "context": null }\n'
)

class Response:
    """ Defines which part of the response is for the user or for the system context.
    params:
        received_message: is expected to be in json format
    """
    def __init__(self, received_message: str):
        self._msg = json.loads(received_message)
        self.message: str = self._msg["response"]
        self.memory_proposal: str | None = self._msg["context"]


class BisbalWrapper():
    def __init__(self):
        self.context: str = INITIAL_CONTEXT
    
    def get_response(self, prompt: str) -> Response:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        self.context +
                        RESPONSE_RULES +
                        INTERACTION_RULES
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.9,
        )
        
        raw = completion.choices[0].message.content
        return Response(raw)
        
    def store_context(self, response: Response):
        # Clear memory if context gets too big.
        # This is done before saving the next proposal in order to remember the last interacion.
        # if len(self.context) > 4000:
        #     self.context = INITIAL_CONTEXT
        
        if response.memory_proposal is not None:
            self.context += f"\n{response.memory_proposal}"
        

# Console test
if __name__ == "__main__":
    bot = BisbalWrapper()

    print("Bisbal ha llegado al servidor. Escribe 'exit' para salir.\n")

    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ("exit", "quit"):
            break

        try:
            response = bot.get_response(user_input)
            print(response._msg)
            bot.store_context(response)
            print(f"\033[92mBisbal: {response.message}\033[0m\n")
        except Exception as e:
            print("⚠️ Error:", e)
            break
