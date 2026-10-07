import { FC} from "react";
import { Composition } from "remotion";
import { Main } from "./Main";
import scenePlan from "./scene-plan.json";

const FPS = typeof scenePlan.project?.fps === "number" ? scenePlan.project.fps : 30;
const WIDTH = typeof scenePlan.project?.width === "number" ? scenePlan.project.width : 1920;
const HEIGHT = typeof scenePlan.project?.height === "number" ? scenePlan.project.height : 1080;
const totalDuration = typeof scenePlan.timing?.total_duration === "number" ? scenePlan.timing.total_duration : 1;
const durationInFrames = Math.max(1, Math.ceil(totalDuration * FPS));

export const Root: FC = () => (
  <Composition
    id="Main"
    component={Main}
    durationInFrames={durationInFrames}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
