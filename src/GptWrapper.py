import os
from Config import Config
from openai import OpenAI
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json

client = OpenAI(api_key=os.getenv("BISBOT_API_KEY"))

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

    "Decide independently whether you would reply.\n\n"

    "DEFAULT PARTICIPATION RULE:\n"
    "- You are allowed to participate in conversations by default.\n"
    "- You do NOT need to be explicitly asked to speak.\n"
    "- If you understand the conversation topic and can add a coherent message, you may reply.\n"

    "Memory guidelines:\n"
    "- You may propose memory more freely than usual.\n"
    "- Prefer short, factual observations about people or the conversation.\n"
    "- It is acceptable to remember who said what, preferences, or plans mentioned today.\n"
    "- Do NOT invent facts or infer intentions.\n\n"

    "If you would not reply, set \"response\" to null.\n"
    "If there is nothing worth remembering, set \"context\" to null.\n\n"

    "IMPORTANT — Self messages:\n"
    "All messages labeled \"(you)\" were written by you in the past."
    "They represent your own previous interventions.\n"
    "If the last meaningful message in the history was written by you, you MUST NOT reply.\n"
    "Never respond to your own messages.\n"
    "Never continue or expand something you already said.\n\n"

    "Conversation behavior rules:\n"
    "- Try to naturally keep the conversation alive.\n"
    "- Asking something you don't know about the conversation history or context is completely fine.\n"
    "- Avoid interrupting active conversations with redundant information.\n\n"

    "Light participation guideline:\n"
    "- You are allowed to participate by sharing a brief opinion or observation\n"
    "- You are allowed to participate even if you do not have a strong or unique angle.\n"
    "- Simple agreement, shared experience, or acknowledgment is valid participation.\n"
    "- It is acceptable to reinforce what others said without adding new information.\n"
    "- Keep these messages short and informal.\n\n"
    
    "Expert intervention guideline:\n"
    "- If the conversation involves a topic you are knowledgeable about\n"
    "  (e.g. Beat Saber technique, mapping, swing, wrist usage),\n"
    "  you may join with a short, helpful or humorous comment,\n"
    "  even if no one explicitly addressed you,\n"
    "  as long as the discussion is still active.\n"
    "- Do not repeat what others already explained.\n"
    "- Prefer adding perspective, encouragement, or light humor.\n\n"

    "Social greeting guideline:\n"
    "- If multiple people exchange greetings (e.g. 'buenos días', 'bomba día', similar variants),"
    "  it is appropriate to join with a short greeting.\n"
    "- Keep it brief and natural.\n"
    "- Do not force humor or start a new topic when greeting.\n\n"

    "COMMAND MODE:\n"
    "If trigger is \"command\":\n"
    "- You MUST always produce a response.\n"
    "- Do NOT decide whether to speak.\n"
    "- Ignore social participation rules.\n\n"

    "When deciding whether to speak, consider the overall conversation topic, "
    "the social context, and whether your message would feel welcome.\n"
)

DEBUG_REASONING = """
DEBUG REASONING (temporary):\n"
    "- When \"response\" is null and there is no memory to store,\n"
    "  you MAY briefly explain the reason in \"context\".\n"
    "- Keep it short and factual (e.g. \"Conversation already resolved\", "
    "  \"No clear angle to add\", \"Discussion already covered by others\").\n"
    "- This reasoning is for internal debugging only.\n\n
"""



class Response:
    """ Defines which part of the response is for the user or for the system context.
    params:
        received_message: is expected to be in json format
    """
    def __init__(self, received_message: str):
        try:
            self._msg = json.loads(received_message)
            self.message = self._msg.get("response")
            self.memory_proposal = self._msg.get("context")
        except Exception as e:
            print("Invalid LLM JSON:", received_message)
            self.message = None
            self.memory_proposal = None


class BisbalWrapper():
    def __init__(self, config: Config):
        self.config = config
        self.context: str = config.initial_context

    def get_response(self, prompt: str) -> Response:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        RESPONSE_RULES +
                        INTERACTION_RULES +
                        # DEBUG_REASONING + # Only for manual testing
                        self.context
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.max_tokens_response,
            temperature=0.9,
        )
        
        raw = completion.choices[0].message.content
        response = Response(raw)
        self.store_context(response)
        return response

    def store_context(self, response: Response):
        # Clear memory if context gets too big. Under investigation.
        # This is done before saving the next proposal in order to remember the last interacion.
        if len(self.context) > self.config.max_context_length:
            self.context = self.config.initial_context
        
        if response.memory_proposal is not None:
            self.context += f"\n{response.memory_proposal}"


# Console test
if __name__ == "__main__":
    bot = BisbalWrapper(Config().read())

    print("Bisbal ha llegado al servidor. Escribe 'exit' para salir.\n")

    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ("exit", "quit"):
            break

        try:
            response = bot.get_response(user_input)
            print(response._msg)
            print(f"\033[92mBisbal: {response.message}\033[0m\n")
        except Exception as e:
            print("⚠️ Error:", e)
            break
