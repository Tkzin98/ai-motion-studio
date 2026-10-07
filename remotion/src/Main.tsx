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
  start?: number;
  end?: number;
  duration?: number;
  timing_source?: string;
  visual?: {
    headline?: string;
    subheadline?: string;
    data?: {
      start_label?: string;
      end_label?: string;
      emphasis?: string;
    };
  };
};

type ScenePlan = {
  version: string;
  director: string;
  scenes: Scene[];
};

const plan = scenePlan as ScenePlan;

const FPS = 30;

const SECONDS_TO_FRAMES = (seconds: number) =>
  Math.round(seconds * FPS);

export const Main: React.FC = () => {
  const frame = useCurrentFrame();

  const currentSceneIndex = plan.scenes.findIndex(
    (scene) => {
      const start = SECONDS_TO_FRAMES(scene.start ?? 0);
      const end = SECONDS_TO_FRAMES(scene.end ?? 0);

      return frame >= start && frame < end;
    }
  );

  const currentScene =
    currentSceneIndex >= 0
      ? plan.scenes[currentSceneIndex]
      : undefined;

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
    SECONDS_TO_FRAMES(currentScene.start ?? 0);

  const sceneEnd =
    SECONDS_TO_FRAMES(currentScene.end ?? 0);

  const localFrame =
    frame - sceneStart;

  const sceneDuration =
    Math.max(sceneEnd - sceneStart, 1);

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
            durationInFrames={sceneDuration}
          >
            <TimelineGraphic
              progress={localFrame / sceneDuration}
              headline={
                currentScene.visual?.headline
              }
              subheadline={
                currentScene.visual?.subheadline
              }
              startLabel={
                currentScene.visual?.data?.start_label
              }
              endLabel={
                currentScene.visual?.data?.end_label
              }
            />
          </Sequence>
        )}
    </AbsoluteFill>
  );
};
