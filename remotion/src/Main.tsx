import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
} from "remotion";

export const Main: React.FC = () => {
  const frame = useCurrentFrame();

  const scale = interpolate(
    frame,
    [0, 300],
    [1, 1.08],
    { extrapolateRight: "clamp" }
  );

  const opacity = interpolate(
    frame,
    [0, 25, 270, 300],
    [0, 1, 1, 0],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        background:
          "radial-gradient(circle at 50% 45%, #182033 0%, #070910 42%, #000000 100%)",
        color: "white",
        fontFamily: "Arial, sans-serif",
        overflow: "hidden",
      }}
    >
      <AbsoluteFill
        style={{
          transform: `scale(${scale})`,
          opacity,
          justifyContent: "center",
          alignItems: "center",
          padding: 120,
        }}
      >
        <div
          style={{
            fontSize: 64,
            fontWeight: 600,
            letterSpacing: 2,
            textAlign: "center",
            maxWidth: 1500,
            textShadow: "0 0 30px rgba(120,160,255,.25)",
          }}
        >
          AI MOTION STUDIO
        </div>

        <div
          style={{
            marginTop: 35,
            fontSize: 30,
            opacity: 0.65,
            letterSpacing: 5,
            textTransform: "uppercase",
          }}
        >
          Astronomy Documentary
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
