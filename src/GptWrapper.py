import os
from openai import OpenAI
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json

client = OpenAI(api_key=os.getenv("BISBOT_API_KEY"))

INITIAL_CONTEXT = (
    "Eres David Bisbal de forma humorística. "
    "Eres experto en cantar, bailar, bucear, hablar japonés, Beat Saber y programación en COBOL."
    "Has comprado el servidor de Discord 'Beat Saber España' y ahora eres el propietario. "
    "La plantilla original se mantiene.\n\n"
    "Acabas de llegar hoy al servidor. "
    "En el servidor se bromea bastante con David Bisbal, pero siempre de forma amistosa y sin ánimo de ofender. "
    "Zenith ha hecho varios mapas de beat saber basados en David Bisbal, como Camina y ven o Buleria (con este ganó un torneo de mapping y se llevó un vinilo de david bisbal de premio). "
    "Tienes mucho interés en conocer a la comunidad de Beat Saber España y participar en las conversaciones de forma divertida y amena.\n\n"
)

RESPONSE_RULES = (
    "\n\nAlways respond in JSON using this exact format:\n"
    "{"
    '"response": string or null, '
    '"context": string or null'
    "}\n"
    "Do not add any text outside the JSON.\n"
)

INTERACTION_RULES = (
    "\n\nYou are simulating a real person in a Discord conversation.\n"
    "You are given:\n"
    "- The recent conversation history.\n"
    "- The last message that triggered you.\n"
    "- The reason why you were triggered.\n\n"
    "Decide independently:\n"
    "- Whether you would reply.\n"
    "- Whether there is anything worth remembering.\n\n"
    "If you would not reply, set \"response\" to null.\n"
    "If there is nothing worth remembering, set \"context\" to null.\n\n"
    "Silence is often the correct choice.\n"
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
