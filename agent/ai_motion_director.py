import json, os, re, sys, time, urllib.error, urllib.request
from pathlib import Path

# AI VIDEO DIRECTOR v6 — 16:9 technology / curiosity documentary
API_KEY = os.environ.get("GEMINI_API_KEY")
MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]
URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
OUT = Path("remotion/src/scene-plan.json")
WPS = 2.6
TYPES = ["kinetic_typography","number_callout","bar_chart","donut_chart","comparison","timeline","process_flow","system_diagram","network","device_blueprint","code_window","quote_card","map_schematic","concept_visual","editorial_card","ambient"]
ANIMS = ["reveal_up","fade","draw","count","grow","stagger","type_on","pulse","orbit_in"]
LAYOUTS = ["center","split","left_focus","right_focus","bottom_band","diagram","full"]
TRANS = ["cut","fade","slide_up","slide_left","wipe"]
BGS = ["black","offwhite","grid","gradient"]
ACCENTS = ["monochrome","cyan","blue","amber","violet","red"]

PROMPT = r"""
Você é um AI Video Director para vídeos horizontais de curiosidade e tecnologia,
com linguagem de documentário editorial premium.

ENTRADA: somente narração com timestamps.
SAÍDA: plano visual completo renderizável em Remotion, 1920x1080, 30 fps.

Pense como diretor + motion designer + designer editorial. Cada segmento recebe
uma cena visual, mas o tratamento deve variar conforme a informação.

Tipos:
kinetic_typography = impacto/frase-chave;
number_callout = número isolado;
bar_chart/donut_chart = dados/percentuais quando houver valores reais;
comparison = dois ou mais itens comparáveis;
timeline = anos/passagem do tempo;
process_flow = etapas em sequência;
system_diagram = como algo funciona;
network = internet, servidores, conexões, IA, dados;
device_blueprint = celular, computador, chip, console ou dispositivo;
code_window = código/algoritmo/comando;
quote_card = frase de impacto;
map_schematic = localização/geografia simplificada;
concept_visual = conceito abstrato;
editorial_card/ambient = pausa, contexto ou transição.

REGRAS:
- NÃO invente números, anos, nomes, rankings, percentuais ou relações factuais.
- Texto na tela deve ser curto e sustentado pela narração.
- Não use gráfico sem dados suficientes.
- Prefira formas, tipografia, diagramas e dispositivos esquemáticos; o vídeo deve
  funcionar sem fotos e vídeos externos.
- Evite repetir o mesmo visual em várias cenas seguidas.
- Animação explica a ideia; não use efeitos infantis ou exagerados.
- Base monocromática + um único acento discreto.
- Os timestamps recebidos são autoridade absoluta e NÃO podem ser alterados.
- Retorne exatamente uma cena por segmento, na mesma ordem.
- Retorne SOMENTE JSON.
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "visual_type": {"type": "string", "enum": TYPES},
                    "purpose": {"type": "string"},
                    "priority": {"type": "string", "enum": ["primary", "supporting", "ambient"]},
                    "layout": {"type": "string", "enum": LAYOUTS},
                    "animation": {"type": "string", "enum": ANIMS},
                    "transition": {"type": "string", "enum": TRANS},
                    "background": {"type": "string", "enum": BGS},
                    "accent": {"type": "string", "enum": ACCENTS},
                    "headline": {"type": "string"},
                    "kicker": {"type": "string"},
                    "subheadline": {"type": "string"},
                    "metric": {"type": "string"},
                    "unit": {"type": "string"},
                    "body": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "value": {"type": "string"},
                                "detail": {"type": "string"}
                            },
                            "required": ["label", "value", "detail"]
                        }
                    },
                    "steps": {"type": "array", "items": {"type": "string"}},
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "value": {"type": "string"},
                                "detail": {"type": "string"}
                            },
                            "required": ["label", "value", "detail"]
                        }
                    },
                    "timeline": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "value": {"type": "string"},
                                "detail": {"type": "string"}
                            },
                            "required": ["label", "value", "detail"]
                        }
                    },
                    "code_lines": {"type": "array", "items": {"type": "string"}},
                    "device": {"type": "string"},
                    "fact_check_required": {"type": "boolean"}
                },
                "required": [
                    "visual_type", "purpose", "priority", "layout", "animation", "transition",
                    "background", "accent", "headline", "kicker", "subheadline", "metric", "unit",
                    "body", "items", "steps", "nodes", "timeline", "code_lines", "device", "fact_check_required"
                ]
            }
        }
    },
    "required": ["scenes"]
}

def ts(s):
    p=s.strip().split(":")
    if len(p)==2: return float(p[0])*60+float(p[1])
    if len(p)==3: return float(p[0])*3600+float(p[1])*60+float(p[2])
    raise ValueError("Timestamp inválido: "+s)

def estimate(text): return max(1.1, len(text.split())/WPS)

def timestamped(text):
    m=list(re.finditer(r"\[(\d{1,2}:\d{2}(?::\d{2})?)\]", text))
    if not m: return None
    out=[]
    for i,x in enumerate(m):
        body=re.sub(r"\s+"," ",text[x.end():m[i+1].start() if i+1<len(m) else len(text)]).strip()
        if not body: continue
        out.append({"id":f"s{len(out)+1:02d}","start":ts(x.group(1)),"end":None,"text":body,"timing_source":"timestamped"})
    for i,s in enumerate(out): s["end"]=out[i+1]["start"] if i+1<len(out) else s["start"]+estimate(s["text"])
    return out

def segments(data):
    if isinstance(data, dict) and isinstance(data.get("segments"), list): raw=data["segments"]
    elif isinstance(data, dict) and isinstance(data.get("narration"), list): raw=data["narration"]
    else:
        text=data.get("narration","") if isinstance(data,dict) else str(data)
        parsed=timestamped(text)
        if parsed: return parsed
        chunks=[x.strip() for x in re.split(r"(?<=[.!?])\s+",text.strip()) if x.strip()]
        cur=0.; parsed=[]
        for c in chunks:
            d=estimate(c); parsed.append({"id":f"s{len(parsed)+1:02d}","start":cur,"end":cur+d,"text":c,"timing_source":"estimated"}); cur+=d
        return parsed
    out=[]; cur=0.
    for item in raw:
        if isinstance(item,str): text=item.strip(); start=cur; end=start+estimate(text); source="estimated"
        else:
            text=str(item.get("text") or item.get("sentence") or "").strip()
            if not text: continue
            start=float(item.get("start",cur)); end=float(item.get("end",start+estimate(text))); source="timestamped" if "start" in item else "estimated"
        out.append({"id":f"s{len(out)+1:02d}","start":max(0,start),"end":max(start+.1,end),"text":text,"timing_source":source}); cur=end
    return out

def call(model, segs):
    blocks=[]
    for i,s in enumerate(segs,1): blocks.append("SEGMENTO %d\nSTART %.3f\nEND %.3f\nTEXT %s"%(i,s["start"],s["end"],s["text"]))
    prompt="""Crie o plano visual. Há uma cena por segmento, em ordem. Não altere tempos. Use apenas informação sustentada pelo texto.\n\n"""+"\n\n".join(blocks)
    payload={"systemInstruction":{"parts":[{"text":PROMPT}]},"contents":[{"role":"user","parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.35,"responseMimeType":"application/json","responseSchema":SCHEMA}}
    req=urllib.request.Request(URL.format(model=model),data=json.dumps(payload).encode(),method="POST",headers={"Content-Type":"application/json","x-goog-api-key":API_KEY})
    with urllib.request.urlopen(req,timeout=120) as r: raw=json.loads(r.read().decode())
    parts=raw.get("candidates",[{}])[0].get("content",{}).get("parts",[])
    text="".join(p.get("text","") for p in parts)
    if not text.strip(): raise RuntimeError("Resposta vazia")
    return json.loads(text)

def safe_scene(raw, source, i):
    raw=raw if isinstance(raw,dict) else {}
    def one(key, allowed, default): return raw.get(key) if raw.get(key) in allowed else default
    vt=one("visual_type",TYPES,"editorial_card")
    visual={k:str(raw.get(k,"")) for k in ["kicker","headline","subheadline","metric","unit","body"]}
    visual["items"]=[{k:str(x.get(k,"")) for k in ["label","value","detail"]} for x in (raw.get("items") if isinstance(raw.get("items"),list) else [])[:6] if isinstance(x,dict)]
    visual["steps"]=[str(x) for x in (raw.get("steps") if isinstance(raw.get("steps"),list) else [])[:8]]
    visual["nodes"]=[{k:str(x.get(k,"")) for k in ["label","value","detail"]} for x in (raw.get("nodes") if isinstance(raw.get("nodes"),list) else [])[:7] if isinstance(x,dict)]
    visual["timeline"]=[{k:str(x.get(k,"")) for k in ["label","value","detail"]} for x in (raw.get("timeline") if isinstance(raw.get("timeline"),list) else [])[:6] if isinstance(x,dict)]
    visual["code_lines"]=[str(x) for x in (raw.get("code_lines") if isinstance(raw.get("code_lines"),list) else [])[:12]]
    visual["device"]=str(raw.get("device","technology"))
    numeric_values=[]
    for item in visual["items"]:
        try: numeric_values.append(float(item["value"].replace(",",".")))
        except Exception: pass
    try: metric_number=float(re.sub(r"[^0-9.-]","",visual["metric"]).replace(",","."))
    except Exception: metric_number=None
    if vt=="bar_chart" and not numeric_values: vt="editorial_card"
    if vt=="donut_chart" and metric_number is None: vt="editorial_card"
    if vt=="comparison" and len(visual["items"])<2: vt="editorial_card"
    if vt=="timeline" and len(visual["timeline"])<2: vt="editorial_card"
    if vt=="process_flow" and len(visual["steps"])<2: vt="editorial_card"
    return {"id":source["id"],"start":round(source["start"],3),"end":round(source["end"],3),"duration":round(source["end"]-source["start"],3),"timing_source":source["timing_source"],"text":source["text"],"visual_type":vt,"purpose":str(raw.get("purpose","")),"priority":one("priority",["primary","supporting","ambient"],"primary"),"layout":one("layout",LAYOUTS,"center"),"animation":one("animation",ANIMS,"fade"),"transition":one("transition",TRANS,"cut"),"background":one("background",BGS,"black"),"accent":one("accent",ACCENTS,"monochrome"),"fact_check_required":bool(raw.get("fact_check_required",False)),"visual":visual}

def main():
    if not API_KEY: raise SystemExit("GEMINI_API_KEY não encontrada.")
    if len(sys.argv)<2: raise SystemExit("Uso: python agent/ai_motion_director.py examples/technology.json")
    try: segs=segments(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    except Exception as e: raise SystemExit("Erro de entrada: "+str(e))
    last=None
    for model in MODELS:
        for attempt in range(1,4):
            try:
                result=call(model,segs); raw=result.get("scenes",[])
                scenes=[safe_scene(raw[i] if i<len(raw) else {},s,i) for i,s in enumerate(segs)]
                plan={"version":"6.0","director":"AI Video Director","project":{"format":"16:9","width":1920,"height":1080,"fps":30,"style":"technology_documentary_editorial"},"timing":{"source":"input_timestamps" if any(s["timing_source"]=="timestamped" for s in segs) else "estimated_from_text","total_duration":round(max(s["end"] for s in segs),3)},"scenes":scenes}
                OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf-8")
                print("AI Video Director v6 — plano salvo em",OUT)
                print("Cenas:",len(scenes),"Duração:",plan["timing"]["total_duration"],"s")
                for s in scenes: print("%s–%s | %s | %s"%(s["start"],s["end"],s["visual_type"],s["animation"]))
                return
            except urllib.error.HTTPError as e:
                last=e; print("HTTP",e.code)
            except Exception as e:
                last=e; print("Erro:",e)
            if attempt<3: time.sleep(2)
    raise SystemExit("Nenhum modelo respondeu: "+str(last))

if __name__=="__main__": main()
