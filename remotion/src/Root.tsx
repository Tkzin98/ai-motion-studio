import React from "react";
import { Composition } from "remotion";
import { Main } from "./Main";

export const Root: React.FC = () => {
  return (
    <Composition
      id="Main"
      component={Main}
      durationInFrames={300}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
