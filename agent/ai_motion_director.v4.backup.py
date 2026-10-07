import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO
# ============================================================

MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

API_BASE = (
    "https://generativelanguage.googleapis.com/v1beta/models"
)

MAX_RETRIES = 3
RETRY_DELAYS = [2, 5, 10]


# ============================================================
# DIRETOR DE MOTION GRAPHICS
# ============================================================

SYSTEM_PROMPT = r"""
Você é um MOTION GRAPHICS DIRECTOR especializado em documentários
cinematográficos de astronomia, ciência e curiosidades.

Você NÃO é um editor de vídeo.

Você NÃO deve decidir:

- qual imagem usar
- qual vídeo usar
- trocar imagens
- trocar footage
- zoom
- movimento de câmera
- enquadramento
- corte
- transição
- música
- efeitos sonoros

Tudo isso será controlado pelo editor.

Sua ÚNICA responsabilidade é analisar a narração e decidir:

1. se um Motion Graphic informacional é realmente necessário;
2. qual tipo de Motion Graphic ajudaria;
3. qual informação o gráfico deve explicar;
4. como essa informação deve ser animada.

============================================================
REGRA MAIS IMPORTANTE
============================================================

NÃO coloque Motion Graphics em todas as frases.

A maioria das frases deve resultar em:

enabled = false
type = none

Um Motion Graphic somente deve existir quando ele acrescentar
informação ou tornar uma ideia significativamente mais fácil
de entender.

NÃO use Motion Graphics simplesmente para deixar o vídeo bonito.

Pense como um diretor de documentário científico.

Pergunte:

"Se eu remover esse Motion Graphic, o espectador perde
alguma compreensão importante?"

Se NÃO:
enabled = false

Se SIM:
enabled = true

============================================================
QUANDO USAR MOTION GRAPHICS
============================================================

Use quando a narração envolver:

- números
- dados
- distâncias
- escalas
- comparações
- proporções
- tempo
- milhões de anos
- bilhões de anos
- órbitas
- trajetórias
- processos
- causa e efeito
- fenômenos científicos
- relações espaciais
- relações entre objetos
- conceitos abstratos
- explicações que seriam difíceis apenas com footage

============================================================
TIPOS PERMITIDOS
============================================================

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

============================================================
EXEMPLOS
============================================================

"Não chove na Lua."

enabled = false
type = none


"Não há vento soprando na superfície."

enabled = false
type = none


"Não há nuvens cruzando o céu."

enabled = false
type = none


"Certas marcas permanecem por milhões de anos."

enabled = true
type = timeline


"A Lua está a 384.400 quilômetros da Terra."

enabled = true
type = distance


"Júpiter é 11 vezes maior que a Terra."

enabled = true
type = comparison


"A Terra leva aproximadamente 365 dias para completar
uma órbita ao redor do Sol."

enabled = true
type = orbit


"O núcleo entra em colapso e libera uma enorme quantidade
de energia."

enabled = true
type = process


"A gravidade mantém os planetas presos às suas órbitas."

enabled = true
type = scientific_diagram


"A superfície parecia completamente desolada."

enabled = false
type = none

============================================================
NÃO INVENTAR
============================================================

NUNCA invente:

- números
- distâncias
- datas
- tamanhos
- velocidades
- massas
- fatos científicos

Use somente informações presentes na narração.

Se um Motion Graphic seria útil, mas faltam dados para construí-lo,
use:

fact_check_required = true

Não invente os dados que estão faltando.

============================================================
ESTÉTICA
============================================================

O resultado será usado em documentários de astronomia.

Estética:

- dark
- cinematográfica
- minimalista
- científica
- premium
- elegante
- moderna
- precisa

Evite:

- PowerPoint
- gráficos corporativos
- excesso de texto
- cores exageradas
- animações infantis
- elementos decorativos sem função
- gráficos genéricos
- excesso de Motion Graphics

O gráfico deve parecer parte de um documentário científico
profissional.

============================================================
ANÁLISE
============================================================

Analise cada segmento da narração individualmente.

Mas também considere o contexto das frases anteriores e posteriores.

Não repita o mesmo Motion Graphic sem necessidade.

Se uma informação já foi explicada visualmente, evite repetir.

O resultado deve ser uma decisão de DIREÇÃO DE MOTION DESIGN,
não uma lista automática de efeitos.
"""


# ============================================================
# JSON SCHEMA
# ============================================================

SCHEMA = {
    "type": "object",
    "properties": {
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer"
                    },

                    "text": {
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

                    "purpose": {
                        "type": "string"
                    },

                    "confidence": {
                        "type": "number"
                    },

                    "fact_check_required": {
                        "type": "boolean"
                    },

                    "graphic": {
                        "type": "object",
                        "properties": {
                            "headline": {
                                "type": "string"
                            },

                            "elements": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },

                            "animation": {
                                "type": "string"
                            },

                            "placement": {
                                "type": "string"
                            },

                            "visual_priority": {
                                "type": "string",
                                "enum": [
                                    "low",
                                    "medium",
                                    "high"
                                ]
                            }
                        },

                        "required": [
                            "headline",
                            "elements",
                            "animation",
                            "placement",
                            "visual_priority"
                        ]
                    }
                },

                "required": [
                    "id",
                    "text",
                    "enabled",
                    "type",
                    "purpose",
                    "confidence",
                    "fact_check_required",
                    "graphic"
                ]
            }
        }
    },

    "required": [
        "segments"
    ]
}


# ============================================================
# PAYLOAD
# ============================================================

def build_payload(narration):

    return {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            SYSTEM_PROMPT
                            + "\n\n"
                            + "NARRAÇÃO PARA ANALISAR:\n\n"
                            + narration
                        )
                    }
                ]
            }
        ],

        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": SCHEMA,
            "temperature": 0.2
        }
    }


# ============================================================
# CHAMADA GEMINI
# ============================================================

def request_model(model, narration):

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:

        print()
        print("ERRO: GEMINI_API_KEY não encontrada.")
        print()
        print("Execute:")
        print()
        print(
            "export GEMINI_API_KEY='SUA_CHAVE_DO_GOOGLE_AI_STUDIO'"
        )
        print()

        sys.exit(1)


    url = f"{API_BASE}/{model}:generateContent"


    payload = build_payload(narration)


    data = json.dumps(
        payload,
        ensure_ascii=False
    ).encode("utf-8")


    request = urllib.request.Request(
        url,
        data=data,

        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        },

        method="POST"
    )


    with urllib.request.urlopen(
        request,
        timeout=180
    ) as response:

        raw = response.read().decode(
            "utf-8"
        )


    result = json.loads(raw)


    try:

        text = (
            result["candidates"][0]
            ["content"]["parts"][0]
            ["text"]
        )

    except (KeyError, IndexError, TypeError):

        raise RuntimeError(
            "A API respondeu, mas não foi possível "
            "encontrar o texto JSON."
        )


    return json.loads(text)


# ============================================================
# RETRY + FALLBACK
# ============================================================

def ask_gemini(narration):

    failures = []


    for model in MODELS:

        print(
            f"→ Tentando modelo: {model}"
        )


        for attempt in range(MAX_RETRIES):

            try:

                result = request_model(
                    model,
                    narration
                )

                print(
                    f"✓ Resposta recebida de {model}"
                )

                return result, model


            except urllib.error.HTTPError as error:

                body = error.read().decode(
                    "utf-8",
                    errors="replace"
                )


                print(
                    f"  HTTP {error.code} "
                    f"(tentativa {attempt + 1}/{MAX_RETRIES})"
                )


                failures.append({
                    "model": model,
                    "status": error.code,
                    "body": body
                })


                # Erros temporários
                if error.code in {
                    429,
                    500,
                    502,
                    503,
                    504
                }:

                    if attempt < MAX_RETRIES - 1:

                        delay = RETRY_DELAYS[
                            min(
                                attempt,
                                len(RETRY_DELAYS) - 1
                            )
                        ]

                        print(
                            f"  Aguardando {delay}s..."
                        )

                        time.sleep(delay)

                        continue


                # Erro permanente
                print(
                    "  Modelo não conseguiu responder."
                )

                break


            except urllib.error.URLError as error:

                print(
                    "  Erro de conexão."
                )

                failures.append({
                    "model": model,
                    "status": "connection",
                    "body": str(error)
                })


                if attempt < MAX_RETRIES - 1:

                    delay = RETRY_DELAYS[
                        min(
                            attempt,
                            len(RETRY_DELAYS) - 1
                        )
                    ]

                    time.sleep(delay)

                    continue

                break


            except TimeoutError:

                print(
                    "  Timeout."
                )

                failures.append({
                    "model": model,
                    "status": "timeout",
                    "body": "timeout"
                })


                if attempt < MAX_RETRIES - 1:

                    time.sleep(
                        RETRY_DELAYS[
                            min(
                                attempt,
                                len(RETRY_DELAYS) - 1
                            )
                        ]
                    )

                    continue

                break


            except json.JSONDecodeError as error:

                print(
                    "  Gemini retornou JSON inválido."
                )

                failures.append({
                    "model": model,
                    "status": "invalid_json",
                    "body": str(error)
                })

                break


            except Exception as error:

                print(
                    f"  Erro: {error}"
                )

                failures.append({
                    "model": model,
                    "status": "unknown",
                    "body": str(error)
                })

                break


        print()


    print()
    print(
        "========================================"
    )
    print(
        "       NENHUM MODELO RESPONDEU"
    )
    print(
        "========================================"
    )
    print()


    for failure in failures:

        print(
            f"{failure['model']} "
            f"→ {failure['status']}"
        )


    print()

    sys.exit(1)


# ============================================================
# VALIDAÇÃO
# ============================================================

def validate_plan(plan):

    if not isinstance(
        plan,
        dict
    ):
        raise ValueError(
            "A resposta não é um objeto JSON."
        )


    segments = plan.get(
        "segments"
    )


    if not isinstance(
        segments,
        list
    ):
        raise ValueError(
            "Campo 'segments' inválido."
        )


    for index, segment in enumerate(
        segments
    ):

        if not isinstance(
            segment,
            dict
        ):
            continue


        segment.setdefault(
            "id",
            index + 1
        )

        segment.setdefault(
            "text",
            ""
        )

        segment.setdefault(
            "enabled",
            False
        )

        segment.setdefault(
            "type",
            "none"
        )

        segment.setdefault(
            "purpose",
            ""
        )

        segment.setdefault(
            "confidence",
            0
        )

        segment.setdefault(
            "fact_check_required",
            False
        )

        segment.setdefault(
            "graphic",
            {
                "headline": "",
                "elements": [],
                "animation": "none",
                "placement": "none",
                "visual_priority": "low"
            }
        )


        # Segurança:
        # se a IA disser que não precisa de gráfico,
        # o tipo obrigatoriamente será NONE.

        if not segment["enabled"]:

            segment["type"] = "none"


    return plan


# ============================================================
# MAIN
# ============================================================

def main():

    if len(sys.argv) < 2:

        print(
            "Uso:"
        )

        print(
            "python agent/ai_motion_director.py "
            "arquivo.json"
        )

        sys.exit(1)


    input_file = Path(
        sys.argv[1]
    )


    if not input_file.exists():

        print(
            f"Arquivo não encontrado: {input_file}"
        )

        sys.exit(1)


    try:

        data = json.loads(
            input_file.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError as error:

        print(
            f"JSON inválido: {error}"
        )

        sys.exit(1)


    narration = data.get(
        "narration"
    )


    if not isinstance(
        narration,
        str
    ):

        print(
            "Erro: 'narration' precisa ser texto."
        )

        sys.exit(1)


    print()
    print(
        "========================================"
    )
    print(
        "        AI MOTION STUDIO"
    )
    print(
        "        AI MOTION DIRECTOR v4"
    )
    print(
        "========================================"
    )
    print()
    print(
        "Analisando a narração..."
    )
    print()


    plan, model = ask_gemini(
        narration
    )


    plan = validate_plan(
        plan
    )


    output = Path(
        "remotion/src/scene-plan.json"
    )


    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    output.write_text(
        json.dumps(
            plan,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )


    segments = plan[
        "segments"
    ]


    active = [
        segment
        for segment in segments
        if segment["enabled"]
    ]


    print()
    print(
        "========================================"
    )
    print(
        "              RESULTADO"
    )
    print(
        "========================================"
    )
    print()

    print(
        f"Modelo: {model}"
    )

    print(
        f"Segmentos: {len(segments)}"
    )

    print(
        f"Motion Graphics: {len(active)}"
    )

    print()


    for segment in segments:

        if segment["enabled"]:

            graphic = segment[
                "graphic"
            ]


            print(
                f"[{segment['id']}] "
                f"{segment['type']} "
                f"| confiança "
                f"{segment['confidence']}"
            )


            print(
                f"    {segment['purpose']}"
            )


            print(
                f"    Gráfico: "
                f"{graphic['headline']}"
            )


            if segment[
                "fact_check_required"
            ]:

                print(
                    "    ⚠ "
                    "fact_check_required=true"
                )


        else:

            print(
                f"[{segment['id']}] "
                f"SEM MOTION GRAPHIC"
            )


    print()

    print(
        "Plano salvo em:"
    )

    print(
        output
    )

    print()


if __name__ == "__main__":
    main()
