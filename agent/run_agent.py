import json
import sys
from pathlib import Path
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END


class MotionState(TypedDict):
    narration: str
    scenes: List[Dict[str, Any]]


def create_plan(state: MotionState):
    narration = state["narration"]

    sentences = [
        s.strip()
        for s in narration.replace("!", ".").replace("?", ".").split(".")
        if s.strip()
    ]

    scenes = []

    for i, sentence in enumerate(sentences):
        scenes.append({
            "id": i + 1,
            "text": sentence,
            "duration": 4,
            "style": "dark_cinematic",
            "motion": "slow_zoom",
            "background": "space"
        })

    return {"scenes": scenes}


graph_builder = StateGraph(MotionState)

graph_builder.add_node("motion_planner", create_plan)

graph_builder.add_edge(START, "motion_planner")
graph_builder.add_edge("motion_planner", END)

graph = graph_builder.compile()


def main():
    if len(sys.argv) < 2:
        print("Uso: python agent/run_agent.py arquivo.json")
        sys.exit(1)

    input_file = Path(sys.argv[1])

    data = json.loads(input_file.read_text(encoding="utf-8"))

    result = graph.invoke({
        "narration": data["narration"],
        "scenes": []
    })

    output = Path("remotion/src/scene-plan.json")

    output.write_text(
        json.dumps(result["scenes"], ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"Plano criado: {output}")
    print(f"Cenas: {len(result['scenes'])}")


if __name__ == "__main__":
    main()
