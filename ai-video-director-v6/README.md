# AI Video Studio

AI Video Director para vídeos horizontais de curiosidades, tecnologia e explicações visuais.

O projeto recebe **somente a narração** e transforma cada trecho em uma cena editorial renderizável pelo Remotion.

## Fluxo

```text
Narração + timestamps
        ↓
AI Video Director v6
        ↓
scene-plan.json
        ↓
Remotion
        ↓
Google Colab
        ↓
MP4 1920x1080
```

## O que o diretor decide

- tipografia cinética
- números e dados
- barras e donuts
- comparações
- timelines
- processos e fluxos
- diagramas de sistemas
- redes e conexões
- dispositivos esquemáticos
- janelas de código
- mapas esquemáticos
- conceitos abstratos
- cards editoriais
- transições e ritmo visual
- fundo, acento e composição

O objetivo não é colocar um efeito em cada frase. Cada segmento recebe uma cena visual, mas o **tipo de visual muda conforme a informação**.

## Entrada recomendada

Use marcadores no próprio campo `narration`:

```json
{
  "narration": "[00:00] Primeira frase...\n[00:04] Segunda frase...\n[00:09] Terceira frase..."
}
```

Também é aceito:

```json
{
  "segments": [
    {"start": 0, "end": 4, "text": "Primeira frase..."},
    {"start": 4, "end": 9, "text": "Segunda frase..."}
  ]
}
```

Os timestamps fornecidos são preservados no plano final. Quando não existem timestamps, o agente estima a duração pelo texto e marca isso como `estimated_from_text`.

## Render

No Google Colab:

```bash
cd /content/ai-motion-studio/remotion
npm ci
npx remotion compositions
npx remotion render src/index.tsx Main out/video.mp4
```

O vídeo é **16:9 horizontal, 1920x1080, 30 fps**.

## Diretor v6

O entrypoint principal agora é:

```bash
python agent/ai_video_director.py examples/technology.json
```

`agent/ai_motion_director.py` e `agent/run_agent.py` continuam existindo como wrappers de compatibilidade e encaminham para o novo diretor.
