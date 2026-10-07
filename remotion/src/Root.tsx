import React from "react";
import { Composition } from "remotion";

import { Main } from "./Main";
import scenePlan from "./scene-plan.json";

const FPS = 30;

const totalDuration =
  typeof scenePlan.timing?.total_duration === "number"
    ? scenePlan.timing.total_duration
    : 1;

const durationInFrames =
  Math.max(1, Math.ceil(totalDuration * FPS));

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
