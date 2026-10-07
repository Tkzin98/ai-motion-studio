import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path


# ============================================================
# AI MOTION STUDIO
# AI MOTION DIRECTOR v5
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
]

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent"
)

OUTPUT_FILE = Path("remotion/src/scene-plan.json")


SYSTEM_PROMPT = r"""
Você é um AI Motion Graphics Director especializado em
documentários cinematográficos de astronomia, ciência e curiosidades.

Sua função NÃO é editar o vídeo inteiro.

Sua função é analisar a NARRAÇÃO e decidir QUANDO um
MOTION GRAPHIC INFORMACIONAL realmente acrescenta
clareza ao que está sendo dito.

IMPORTANTE:

NÃO escolha imagens.
NÃO escolha vídeos.
NÃO escolha zoom de câmera.
NÃO escolha enquadramento.
NÃO escolha cortes.
NÃO escolha transições.
NÃO escolha música.
NÃO escolha efeitos sonoros.

O material visual principal já será controlado pelo editor.

Você controla APENAS motion graphics informacionais.

Use motion graphics somente quando eles ajudarem o espectador
a compreender uma informação que seria difícil visualizar
apenas com imagens ou vídeo.

Exemplos de informações que podem justificar motion graphics:

- números
- dados
- porcentagens
- distâncias
- escalas
- comparações
- passagem de tempo
- milhões ou bilhões de anos
- tamanho de planetas, estrelas ou objetos
- órbitas
- trajetórias
- processos científicos
- relações entre objetos
- fenômenos físicos
- conceitos abstratos
- explicações científicas
- localização espacial
- evolução de um fenômeno
- sequências ou etapas

NÃO crie motion graphics para todas as frases.

Na maioria das frases, a resposta deve ser:

enabled = false
type = "none"

Um documentário profissional NÃO deve parecer um
template que coloca gráficos em cada frase.

Exemplo:

"Não há vento soprando na superfície da Lua."

Normalmente:
enabled = false

Porque a própria imagem da superfície lunar pode comunicar isso.

Outro exemplo:

"Certas marcas permanecem por milhões de anos."

Pode justificar um gráfico temporal mostrando a enorme
escala de tempo envolvida.

ESTILO VISUAL:

- dark
- cinematográfico
- científico
- minimalista
- premium
- elegante
- moderno
- preciso
- discreto
- documental

Evite estética infantil, exagerada, colorida demais ou
parecida com vídeo de propaganda.

As animações devem ser suaves e intencionais.

TIPOS PERMITIDOS:

none
data_callout
comparison
scale
distance
timeline
orbit
trajectory
process
scientific_diagram
concept_visualization
label_callout

ANIMAÇÕES PERMITIDAS:

none
progressive_reveal
line_draw
counter
scale_in
trajectory_draw
diagram_build
fade_rise

POSICIONAMENTOS PERMITIDOS:

none
center
upper_left
upper_right
lower_left
lower_right
lower_third

INTENSIDADE:

subtle
moderate

Use "subtle" como padrão.

NUNCA invente dados científicos.

Quando uma informação precisar de confirmação externa,
marque:

fact_check_required = true

Preserve exatamente o texto original da frase.

A resposta deve ser JSON válido.
Não escreva explicações fora do JSON.
"""


RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "sentence": {
                        "type": "string"
                    },
                    "enabled": {
                        "type": "boolean"
                    },
                    "type": {
                        "type": "string",
                        "enum": [
                            "none",
                            "data_callout",
                            "comparison",
                            "scale",
                            "distance",
                            "timeline",
                            "orbit",
                            "trajectory",
                            "process",
                            "scientific_diagram",
                            "concept_visualization",
                            "label_callout"
                        ]
                    },
                    "reason": {
                        "type": "string"
                    },
                    "animation": {
                        "type": "string",
                        "enum": [
                            "none",
                            "progressive_reveal",
                            "line_draw",
                            "counter",
                            "scale_in",
                            "trajectory_draw",
                            "diagram_build",
                            "fade_rise"
                        ]
                    },
                    "placement": {
                        "type": "string",
                        "enum": [
                            "none",
                            "center",
                            "upper_left",
                            "upper_right",
                            "lower_left",
                            "lower_right",
                            "lower_third"
                        ]
                    },
                    "intensity": {
                        "type": "string",
                        "enum": [
                            "subtle",
                            "moderate"
                        ]
                    },
                    "fact_check_required": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "sentence",
                    "enabled",
                    "type",
                    "reason",
                    "animation",
                    "placement",
                    "intensity",
                    "fact_check_required"
                ]
            }
        }
    },
    "required": [
        "scenes"
    ]
}

def call_gemini(model, narration):
    """Envia a narração para o Gemini e retorna o JSON."""

    url = API_URL.format(model=model)

    user_prompt = f"""
Analise a seguinte narração de documentário:

--- NARRAÇÃO ---
{narration}
--- FIM DA NARRAÇÃO ---

Divida a narração em frases ou unidades de sentido.

Para cada unidade, decida se um motion graphic
informacional realmente acrescenta compreensão.

Se não acrescentar, use:
enabled=false
type="none"
animation="none"
placement="none"

Se acrescentar, escolha o tipo mais adequado.

Não invente informações que não estejam na narração.

Retorne somente o JSON solicitado pelo schema.
"""

    payload = {
        "systemInstruction": {
            "parts": [
                {
                    "text": SYSTEM_PROMPT
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": user_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA
        }
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            raw = response.read().decode("utf-8")

        result = json.loads(raw)

        candidates = result.get("candidates", [])

        if not candidates:
            raise RuntimeError(
                "Gemini não retornou nenhum candidato."
            )

        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        text = ""

        for part in parts:
            if "text" in part:
                text += part["text"]

        if not text.strip():
            raise RuntimeError(
                "Gemini retornou uma resposta vazia."
            )

        return json.loads(text)

    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")

        print(
            f"  HTTP {error.code}: "
            f"{body[:500]}"
        )

        raise

    except urllib.error.URLError as error:
        print(
            f"  Erro de conexão: {error.reason}"
        )
        raise


def normalize_plan(plan):
    """Garante valores seguros para o Remotion."""

    scenes = plan.get("scenes", [])

    if not isinstance(scenes, list):
        raise ValueError(
            "Resposta inválida: scenes não é uma lista."
        )

    allowed_types = {
        "none",
        "data_callout",
        "comparison",
        "scale",
        "distance",
        "timeline",
        "orbit",
        "trajectory",
        "process",
        "scientific_diagram",
        "concept_visualization",
        "label_callout",
    }

    normalized = []

    for scene in scenes:
        if not isinstance(scene, dict):
            continue

        enabled = bool(scene.get("enabled", False))

        graphic_type = scene.get("type", "none")

        if graphic_type not in allowed_types:
            graphic_type = "none"
            enabled = False

        if not enabled:
            graphic_type = "none"

        normalized.append(
            {
                "sentence": str(
                    scene.get("sentence", "")
                ),
                "enabled": enabled,
                "type": graphic_type,
                "reason": str(
                    scene.get("reason", "")
                ),
                "animation": str(
                    scene.get("animation", "none")
                ),
                "placement": str(
                    scene.get("placement", "none")
                ),
                "intensity": str(
                    scene.get("intensity", "subtle")
                ),
                "fact_check_required": bool(
                    scene.get(
                        "fact_check_required",
                        False
                    )
                ),
            }
        )

    return {
        "version": "5.0",
        "director": "AI Motion Director",
        "scenes": normalized,
    }


def save_plan(plan):
    """Salva o plano para o Remotion."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            plan,
            file,
            ensure_ascii=False,
            indent=2
        )


def load_narration(path):
    """Lê o arquivo de entrada."""

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    narration = data.get("narration")

    if not narration:
        raise ValueError(
            "O arquivo não possui o campo 'narration'."
        )

    return narration



def print_summary(plan):
    scenes = plan.get("scenes", [])

    enabled = [
        scene
        for scene in scenes
        if scene.get("enabled") is True
    ]

    print()
    print("=" * 50)
    print("       MOTION GRAPHICS DETECTADOS")
    print("=" * 50)

    print(f"Frases analisadas: {len(scenes)}")
    print(f"Motion graphics:   {len(enabled)}")
    print(
        f"Sem motion:        "
        f"{len(scenes) - len(enabled)}"
    )

    print()

    for index, scene in enumerate(scenes, 1):
        status = (
            "MOTION"
            if scene["enabled"]
            else "SEM MOTION"
        )

        print(
            f"[{index:02d}] {status} | "
            f"{scene['type']}"
        )

        sentence = scene["sentence"].strip()

        if len(sentence) > 100:
            sentence = sentence[:97] + "..."

        print(f"     {sentence}")

        if scene["enabled"]:
            print(
                f"     animação: "
                f"{scene['animation']}"
            )
            print(
                f"     posição:  "
                f"{scene['placement']}"
            )

        if scene["fact_check_required"]:
            print(
                "     ⚠ fact-check necessário"
            )

        print()


def run():
    if not API_KEY:
        print()
        print("=" * 50)
        print("ERRO: GEMINI_API_KEY NÃO ENCONTRADA")
        print("=" * 50)
        print()
        print(
            "Defina sua chave antes de executar:"
        )
        print()
        print(
            "export GEMINI_API_KEY='SUA_CHAVE'"
        )
        print()
        sys.exit(1)

    if len(sys.argv) < 2:
        print()
        print(
            "Uso:"
        )
        print(
            "python agent/ai_motion_director.py "
            "examples/moon.json"
        )
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        narration = load_narration(input_file)
    except Exception as error:
        print()
        print(
            f"Erro ao ler entrada: {error}"
        )
        sys.exit(1)

    print()
    print("=" * 50)
    print("        AI MOTION STUDIO")
    print("        AI MOTION DIRECTOR v5")
    print("=" * 50)
    print()
    print("Analisando a narração...")
    print()
    print(
        "Objetivo: encontrar apenas informações "
        "que realmente se beneficiam de "
        "motion graphics."
    )
    print()

    last_error = None

    for model in MODELS:
        print(
            f"→ Tentando modelo: {model}"
        )

        for attempt in range(1, 4):
            try:
                print(
                    f"  tentativa {attempt}/3"
                )

                plan = call_gemini(
                    model,
                    narration
                )

                plan = normalize_plan(plan)

                save_plan(plan)

                print()
                print(
                    f"✓ Modelo respondeu: {model}"
                )

                print_summary(plan)

                print("=" * 50)
                print(
                    "PLANO SALVO COM SUCESSO"
                )
                print("=" * 50)
                print()
                print(
                    f"Arquivo: {OUTPUT_FILE}"
                )
                print()

                return

            except Exception as error:
                last_error = error

                if attempt < 3:
                    time.sleep(2)

        print(
            f"  Modelo não conseguiu responder."
        )
        print()

    print("=" * 50)
    print("       NENHUM MODELO RESPONDEU")
    print("=" * 50)
    print()
    print(
        "Verifique a chave da API, "
        "a conexão e a disponibilidade "
        "dos modelos."
    )
    print()

    if last_error:
        print(
            f"Último erro: {last_error}"
        )

    sys.exit(1)


if __name__ == "__main__":
    run()
