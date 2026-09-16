import json, pandas as pd
d = json.load(open("../20_evidencia/E05_app/zap_full_juiceshop.json"))
alertas = [{"riesgo": a["riskdesc"].split(" ")[0], "alerta": a["alert"],
            "cwe": a.get("cweid"), "instancias": len(a.get("instances", [])),
            "solucion": a.get("solution","")[:120]}
           for s in d["site"] for a in s["alerts"]]
df = pd.DataFrame(alertas).sort_values("instancias", ascending=False)
df.to_csv("../40_hallazgos/PT05_alertas_zap.csv", index=False)
print(df.groupby("riesgo").size().to_string())
print(df.head(12).to_string(index=False))