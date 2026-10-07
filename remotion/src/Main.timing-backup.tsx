import React from "react";
import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
} from "remotion";

import { TimelineGraphic } from "./motion/TimelineGraphic";

import scenePlan from "./scene-plan.json";

type Scene = {
  sentence: string;
  enabled: boolean;
  type: string;
  reason: string;
  animation: string;
  placement: string;
  intensity: string;
  fact_check_required: boolean;
};

type ScenePlan = {
  version: string;
  director: string;
  scenes: Scene[];
};

const plan = scenePlan as ScenePlan;

const FPS = 30;

const SCENE_DURATION = 90;

export const Main: React.FC = () => {
  const frame = useCurrentFrame();

  const currentSceneIndex = Math.floor(
    frame / SCENE_DURATION
  );

  const currentScene =
    plan.scenes[currentSceneIndex];

  if (!currentScene) {
    return (
      <AbsoluteFill
        style={{
          background: "#000000",
        }}
      />
    );
  }

  const sceneStart =
    currentSceneIndex * SCENE_DURATION;

  const localFrame =
    frame - sceneStart;

  return (
    <AbsoluteFill
      style={{
        background: "#000000",
        overflow: "hidden",
      }}
    >
      {/* =====================================================
          ÁREA RESERVADA PARA O VÍDEO/IMAGEM PRINCIPAL
          O sistema NÃO controla o footage.
         ===================================================== */}

      <AbsoluteFill />

      {/* =====================================================
          MOTION GRAPHICS
         ===================================================== */}

      {currentScene.enabled &&
        currentScene.type === "timeline" && (
          <Sequence
            from={0}
            durationInFrames={SCENE_DURATION}
          >
            <TimelineGraphic
              progress={localFrame / SCENE_DURATION}
            />
          </Sequence>
        )}
    </AbsoluteFill>
  );
};
