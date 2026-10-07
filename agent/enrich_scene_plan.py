import json
from pathlib import Path

INPUT = Path("remotion/src/scene-plan.json")
OUTPUT = Path("remotion/src/scene-plan.json")

WORDS_PER_SECOND = 2.6
MIN_DURATION = 1.2
PAUSE_BETWEEN_SCENES = 0.18


def estimate_duration(sentence: str) -> float:
    words = len(sentence.split())
    duration = words / WORDS_PER_SECOND
    return max(MIN_DURATION, duration)


def build_visual(scene):
    if not scene.get("enabled"):
        return {
            "headline": "",
            "subheadline": "",
            "data": {},
        }

    sentence = scene.get("sentence", "")
    scene_type = scene.get("type", "none")

    if scene_type == "timeline":
        return {
            "headline": "MILHÕES DE ANOS",
            "subheadline": "Uma marca pode permanecer preservada por uma escala de tempo extrema.",
            "data": {
                "start_label": "PEGADA",
                "end_label": "MILHÕES DE ANOS",
                "emphasis": "escala temporal",
            },
        }

    if scene_type == "scale":
        return {
            "headline": sentence,
            "subheadline": "Comparação de escala",
            "data": {},
        }

    if scene_type == "distance":
        return {
            "headline": sentence,
            "subheadline": "Escala de distância",
            "data": {},
        }

    if scene_type == "comparison":
        return {
            "headline": sentence,
            "subheadline": "Comparação visual",
            "data": {},
        }

    if scene_type == "orbit":
        return {
            "headline": sentence,
            "subheadline": "Trajetória orbital",
            "data": {},
        }

    if scene_type == "trajectory":
        return {
            "headline": sentence,
            "subheadline": "Trajetória",
            "data": {},
        }

    if scene_type == "process":
        return {
            "headline": sentence,
            "subheadline": "Processo",
            "data": {},
        }

    if scene_type == "scientific_diagram":
        return {
            "headline": sentence,
            "subheadline": "Diagrama científico",
            "data": {},
        }

    if scene_type == "concept_visualization":
        return {
            "headline": sentence,
            "subheadline": "Conceito científico",
            "data": {},
        }

    if scene_type == "data_callout":
        return {
            "headline": sentence,
            "subheadline": "Dado relevante",
            "data": {},
        }

    if scene_type == "label_callout":
        return {
            "headline": sentence,
            "subheadline": "Informação",
            "data": {},
        }

    return {
        "headline": "",
        "subheadline": "",
        "data": {},
    }


def enrich():
    if not INPUT.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {INPUT}")

    with INPUT.open("r", encoding="utf-8") as f:
        plan = json.load(f)

    current_time = 0.0

    for scene in plan.get("scenes", []):
        duration = estimate_duration(scene.get("sentence", ""))

        scene["start"] = round(current_time, 2)
        scene["end"] = round(current_time + duration, 2)
        scene["duration"] = round(duration, 2)
        scene["timing_source"] = "estimated"

        scene["visual"] = build_visual(scene)

        current_time += duration + PAUSE_BETWEEN_SCENES

    plan["timing"] = {
        "source": "estimated_from_text",
        "total_duration": round(max(current_time - PAUSE_BETWEEN_SCENES, 0), 2),
        "words_per_second": WORDS_PER_SECOND,
    }

    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

    print("Plano enriquecido com sucesso.")
    print(f"Duração estimada: {plan['timing']['total_duration']}s")

    for i, scene in enumerate(plan.get("scenes", []), 1):
        print(
            f"{i}. "
            f"{scene['start']:.2f}s → {scene['end']:.2f}s | "
            f"{scene['type']} | "
            f"{'MG' if scene['enabled'] else 'sem MG'}"
        )


if __name__ == "__main__":
    enrich()
