import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from GptWrapper import BisbalWrapper

def test_formatted_history(history: str):
    bot = BisbalWrapper()

    payload = {
        "trigger": "conversation_activity",
        "history": history
    }

    prompt = json.dumps(payload, indent=2, ensure_ascii=False)
    response = bot.get_response(prompt)

    print("Response:", response.message)
    print("Context:", response.memory_proposal)


history1 = """
    Juan: alguien ha probado el nuevo mapa?
    Ana: sí, pero el drop es raro
    Juan: es muy largo
    Bisbal: jajaja ya ves
    Ana: totalmente
""".strip()

history2 = """
    Splash Dance Pattern: Brother sería la 4° vez que reinstalo un sistema operativo Linux
    Yo: Yo lo voy a probar y si necesita, si se lo cambio
    Tech's dog: vale la pena risk of rain sin dlcs??
    Tech's dog: me lo compre por 4€ xd
    Ludicrous speed ahhhhhhh pattern: quieres hechar una partida? que estoy con un colega a punto de jugarlo
    Tech's dog: si quieres
    Tech's dog: no se nada
    Tech's dog: llevo una run
    Ludicrous speed ahhhhhhh pattern: agregame y te meto al voice chat
    Ksum Nole: ugh?
    おいおいおい MEOW: 102%
    Splash Dance Pattern: Bomba dia
    Rex: Bombona dia
    The Master (of functions): bobomb dia
    Ksum Nole: Bombeta dia
""".strip()

history3 = """
    Splash Dance Pattern: Brother sería la 4° vez que reinstalo un sistema operativo Linux
    Yo: Yo lo voy a probar y si necesita, si se lo cambio
    Tech's dog: vale la pena risk of rain sin dlcs??
    Tech's dog: me lo compre por 4€ xd
    Ludicrous speed ahhhhhhh pattern: quieres hechar una partida? que estoy con un colega a punto de jugarlo
    Tech's dog: si quieres
    Tech's dog: no se nada
    Tech's dog: llevo una run
    Ludicrous speed ahhhhhhh pattern: agregame y te meto al voice chat
    Ksum Nole: ugh?
    おいおいおい MEOW: 102%
    Splash Dance Pattern: Bomba dia
    Rex: Bombona dia
    The Master (of functions): bobomb dia
    David Bisbal(you): ¡Bombeta día a todos! Estoy aquí para alegrar un poco la conversación. ¿Alguien quiere hablar de música o de Beat Saber? 🎶
    Ksum Nole: Bombeta dia
""".strip()

history4 = """
Rex: Soy ciego
Rex: E imbecil
Rex: Ignorenme

The Master (of functions): 
Limpiaparabrisas Bosch: xd
Limpiaparabrisas Bosch: https://replay.beatleader.com/?scoreId=28568255
ayuda no sé si me estoy fumando yo algo pero noto que estoy haciendo el swing algo outward?
Ksum Nole: A ver creo que el giroscopio de tus gafas se rompió porque cuando juegas te pones mirando a cuenca
Rex: no, de hecho estás apuntando super para dentro y parece que ni usas muñeca, no rotas la muñeca y simplemente reposicionas tu brazo causando que hagas un swing como un parabrisas
Limpiaparabrisas Bosch: Grax, intentaré usar más muñeca
Ksum Nole: https://replay.beatleader.com/?scoreId=27168082
que le pasa a este pobre
tiene un swing que ni yo
y saca más acc igualmente que mis plays
Placa nRF52840: quizás haciendo más swing superas a casi toda España
""".strip()

history5 = """
Rex: momento navidad
Rex: xd
Rex: seguro que ya en enero/febrero abren

The Master (of functions): Yea ahah entendible

Deir: en mis tiempos la gente se hacía del ranking team para tener una cola y cerrarla
Deir: @(Washed) Cobayo
Deir: prácticamente el trabajo lo hacían los estudiantes

Rex: xddd
Rex: el cobayo tenía la cola de ranking más troll que he leído en mi vida
Rex: porque tenía tantas restricciones que prácticamente solo 3 mappers podían mandarle mapas LMAO

Deir: yep todos tenían las colas cerradas y solo aceptaban los mapas que querían xd
Deir: imagino que sigue un poco así

Rex: tristemente muchos siguen siendo así
Rex: sé que algunos aceptan nuevos mappers
Rex: pero sigue siendo difícil
""".strip()

history6 = """
Rex: también te digo que ahora hay estándares de calidad más altos
Rex: entonces para tener tu mapa rankeado tienes que tener bastante buena calidad de mapa en el 99% de los casos
(Washed) Cobayo: Bien hecho llorando en la llorería
(Washed) Cobayo: yo moddeo mapas que me gusten
(Washed) Cobayo: o sea mapas de complex frequency
Deir: pero como es esto de que bisbal ha comprado el server?
""".strip()

history7 = """
Rex: también te digo que ahora hay estándares de calidad más altos
Rex: entonces para tener tu mapa rankeado tienes que tener bastante buena calidad de mapa en el 99% de los casos
(Washed) Cobayo: Bien hecho llorando en la llorería
(Washed) Cobayo: yo moddeo mapas que me gusten
(Washed) Cobayo: o sea mapas de complex frequency
Deir: pero como es esto de que bisbal ha comprado el server?
David Bisbal(you): ¡Hola a todos! Sí, he aterrizado en el servidor y estoy listo para disfrutar de la buena música y los buenos mapas. Y hablando de mapas, ¡me encanta saber que hay tanta calidad en lo que hacen! ¿Quién tiene un mapa favorito para que lo probemos juntos?
Rex: oye bisbal, como hago un contador en COBOL?
""".strip()

if __name__ == "__main__":
    test_formatted_history(history3)
