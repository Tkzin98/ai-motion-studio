import React from "react";
import { Composition } from "remotion";

import { Main } from "./Main";
import scenePlan from "./scene-plan.json";

const FPS = 30;
const SCENE_DURATION = 90;

const sceneCount =
  Array.isArray(scenePlan.scenes)
    ? scenePlan.scenes.length
    : 1;

const durationInFrames =
  Math.max(sceneCount, 1) *
  SCENE_DURATION;

export const Root: React.FC = () => {
  return (
    <Composition
      id="Main"
      component={Main}
      durationInFrames={durationInFrames}
      fps={FPS}
      width={1920}
      height={1080}
    />
  );
};
