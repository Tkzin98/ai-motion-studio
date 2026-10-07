import { FC} from "react";
import { AbsoluteFill, Sequence, useVideoConfig } from "remotion";
import { DirectorScene, DirectorSceneData } from "./motion/DirectorScene";
import scenePlan from "./scene-plan.json";

type Scene = DirectorSceneData & {
  id: string;
  start: number;
  end: number;
  duration: number;
  timing_source?: string;
  text?: string;
};

type ScenePlan = {
  version: string;
  director: string;
  project?: {
    format?: string;
    width?: number;
    height?: number;
    fps?: number;
  };
  timing?: {
    total_duration?: number;
  };
  scenes: Scene[];
};

const plan = scenePlan as ScenePlan;

export const Main: FC = () => {
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill style={{ background: "#050505", overflow: "hidden" }}>
      {plan.scenes.map((scene) => {
        const startFrame = Math.round(scene.start * fps);
        const durationInFrames = Math.max(1, Math.round((scene.end - scene.start) * fps));
        return (
          <Sequence key={scene.id} from={startFrame} durationInFrames={durationInFrames}>
            <DirectorScene scene={scene} durationInFrames={durationInFrames} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
