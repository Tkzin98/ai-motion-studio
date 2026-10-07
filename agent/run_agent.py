import json
import re
import sys
from pathlib import Path


def clean_sentences(narration: str):
    return [
        s.strip()
        for s in re.split(r"[.!?]+", narration)
        if s.strip()
    ]


def has_any(text: str, words):
    return any(word in text for word in words)


def analyze_motion_need(sentence: str, index: int):
    text = sentence.lower()

    # 1. Linha do tempo / passagem de tempo
    if has_any(text, [
        "milhões de anos",
        "bilhões de anos",
        "milhares de anos",
        "milhões",
        "bilhões",
        "anos",
        "século",
        "tempo",
    ]):
        return {
            "enabled": True,
            "type": "timeline",
            "priority": "high",
            "reason": "A narração apresenta uma escala temporal relevante.",
            "design": {
                "title": "Escala de tempo",
                "elements": [
                    "linha do tempo",
                    "marcadores temporais",
                    "destaque progressivo"
                ],
                "animation": "progressive_reveal",
                "text_emphasis": "tempo",
            }
        }

    # 2. Comparação / escala
    if has_any(text, [
        "maior",
        "menor",
        "maior que",
        "menor que",
        "comparado",
        "comparação",
        "vezes maior",
        "vezes menor",
        "distância",
        "milhões de quilômetros",
        "quilômetros",
    ]):
        return {
            "enabled": True,
            "type": "comparison",
            "priority": "high",
            "reason": "A frase envolve comparação ou escala.",
            "design": {
                "title": "Comparação visual",
                "elements": [
                    "objetos em escala",
                    "linha de medida",
                    "rótulos comparativos"
                ],
                "animation": "staggered_build",
                "text_emphasis": "escala",
            }
        }

    # 3. Números / dados
    if re.search(r"\d", sentence) or has_any(text, [
        "porcentagem",
        "percentual",
        "temperatura",
        "velocidade",
        "massa",
        "diâmetro",
        "distância",
        "quantidade",
    ]):
        return {
            "enabled": True,
            "type": "data_callout",
            "priority": "high",
            "reason": "Existe um dado quantitativo que pode ser reforçado visualmente.",
            "design": {
                "title": "Dado científico",
                "elements": [
                    "número principal",
                    "unidade",
                    "rótulo contextual"
                ],
                "animation": "count_up",
                "text_emphasis": "number",
            }
        }

    # 4. Fenômeno ou processo científico
    if has_any(text, [
        "formação",
        "se forma",
        "formado",
        "órbita",
        "orbita",
        "colisão",
        "explosão",
        "gravidade",
        "radiação",
        "erosão",
        "evaporação",
        "fusão",
        "rotação",
        "translação",
        "movimento",
        "processo",
    ]):
        return {
            "enabled": True,
            "type": "scientific_diagram",
            "priority": "high",
            "reason": "A frase explica um fenômeno ou processo científico.",
            "design": {
                "title": "Explicação científica",
                "elements": [
                    "diagrama",
                    "setas explicativas",
                    "rótulos",
                    "relações entre elementos"
                ],
                "animation": "build_in_sequence",
                "text_emphasis": "concept",
            }
        }

    # 5. Condições físicas importantes
    if has_any(text, [
        "sem vento",
        "não há vento",
        "sem atmosfera",
        "não há atmosfera",
        "sem água",
        "não há água",
        "sem nuvens",
        "não há nuvens",
        "sem chuva",
        "não chove",
        "tempestade",
    ]):
        return {
            "enabled": True,
            "type": "fact_diagram",
            "priority": "medium",
            "reason": "A frase apresenta uma condição física que pode ser explicada visualmente.",
            "design": {
                "title": "Condição física",
                "elements": [
                    "ícone ou símbolo científico",
                    "rótulo curto",
                    "indicação visual de ausência/presença"
                ],
                "animation": "minimal_reveal",
                "text_emphasis": "fact",
            }
        }

    # 6. Por padrão: não inventar Motion Graphics
    return {
        "enabled": False,
        "type": "none",
        "priority": "none",
        "reason": "A imagem/narração pode comunicar a ideia sem Motion Graphics adicional.",
        "design": None,
    }


def create_plan(narration: str):
    sentences = clean_sentences(narration)
    scenes = []

    for index, sentence in enumerate(sentences):
        graphics = analyze_motion_need(sentence, index)

        scenes.append({
            "id": index + 1,
            "text": sentence,
            "duration": 4,

            # O agente NÃO controla:
            "media": {
                "change_image": False,
                "change_video": False,
                "camera_motion": False,
                "zoom": False,
                "transition": False,
            },

            # O agente controla SOMENTE Motion Graphics:
            "motion_graphics": graphics
        })

    return scenes


def main():
    if len(sys.argv) < 2:
        print("Uso: python agent/run_agent.py arquivo.json")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    if not input_file.exists():
        print(f"Arquivo não encontrado: {input_file}")
        sys.exit(1)

    try:
        data = json.loads(
            input_file.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        print(f"JSON inválido: {error}")
        sys.exit(1)

    if "narration" not in data:
        print("Erro: o JSON precisa conter o campo 'narration'.")
        sys.exit(1)

    scenes = create_plan(data["narration"])

    output = Path("remotion/src/scene-plan.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        json.dumps(
            scenes,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    active = sum(
        1 for scene in scenes
        if scene["motion_graphics"]["enabled"]
    )

    print()
    print("========================================")
    print("        AI MOTION STUDIO")
    print("        MOTION DIRECTOR v2")
    print("========================================")
    print()
    print(f"Narração: {input_file}")
    print(f"Cenas analisadas: {len(scenes)}")
    print(f"Cenas com Motion Graphics: {active}")
    print()

    for scene in scenes:
        mg = scene["motion_graphics"]

        if mg["enabled"]:
            print(
                f"[{scene['id']}] "
                f"MG: {mg['type']} "
                f"({mg['priority']})"
            )
        else:
            print(
                f"[{scene['id']}] "
                f"MG: nenhum"
            )

    print()
    print(f"Plano salvo em: {output}")
    print()


if __name__ == "__main__":
    main()
