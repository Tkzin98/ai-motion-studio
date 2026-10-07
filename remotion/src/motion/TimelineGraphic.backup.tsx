import React from "react";
import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
} from "remotion";

type Props = {
  progress?: number;
};

export const TimelineGraphic: React.FC<Props> = ({
  progress = 1,
}) => {
  const frame = useCurrentFrame();

  const reveal = interpolate(
    frame,
    [0, 18],
    [0, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  const opacity = interpolate(
    frame,
    [0, 10, 75, 90],
    [0, 1, 1, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  const lineWidth = `${reveal * 100}%`;

  const dotScale = interpolate(
    frame,
    [8, 20],
    [0.2, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: 150,
        pointerEvents: "none",
        opacity,
      }}
    >
      <div
        style={{
          width: 1250,
          height: 150,
          position: "relative",
          fontFamily:
            "Arial, Helvetica, sans-serif",
        }}
      >
        {/* linha de fundo */}
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: 70,
            height: 2,
            background:
              "rgba(255,255,255,0.18)",
          }}
        />

        {/* linha progressiva */}
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 69,
            height: 4,
            width: lineWidth,
            background:
              "linear-gradient(90deg, #ffffff, #8fb8ff)",
            boxShadow:
              "0 0 18px rgba(143,184,255,0.35)",
          }}
        />

        {/* ponto inicial */}
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 59,
            width: 24,
            height: 24,
            borderRadius: "50%",
            background: "#ffffff",
            transform:
              `scale(${dotScale})`,
            boxShadow:
              "0 0 20px rgba(255,255,255,0.45)",
          }}
        />

        {/* ponto final */}
        <div
          style={{
            position: "absolute",
            right: 0,
            top: 59,
            width: 24,
            height: 24,
            borderRadius: "50%",
            background: "#8fb8ff",
            transform:
              `scale(${dotScale})`,
            boxShadow:
              "0 0 24px rgba(143,184,255,0.5)",
          }}
        />

        {/* texto inicial */}
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            fontSize: 22,
            letterSpacing: 1,
            color:
              "rgba(255,255,255,0.72)",
          }}
        >
          PEGADA
        </div>

        <div
          style={{
            position: "absolute",
            left: 0,
            top: 92,
            fontSize: 18,
            color:
              "rgba(255,255,255,0.45)",
          }}
        >
          décadas
        </div>

        {/* texto final */}
        <div
          style={{
            position: "absolute",
            right: 0,
            top: 0,
            fontSize: 22,
            letterSpacing: 1,
            color:
              "rgba(255,255,255,0.72)",
            textAlign: "right",
          }}
        >
          TEMPO
        </div>

        <div
          style={{
            position: "absolute",
            right: 0,
            top: 92,
            fontSize: 18,
            color:
              "rgba(255,255,255,0.45)",
            textAlign: "right",
          }}
        >
          milhões de anos
        </div>
      </div>
    </AbsoluteFill>
  );
};
