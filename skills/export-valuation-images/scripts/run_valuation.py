import json, sys
from valuation.core import load_state, calculate_valuation_batch

state = load_state()
sector_funds = {}
sector_alias = {}

for sector in state.get("sectors", []):
    name = sector["name"]
    codes = [f["code"] for f in sector.get("funds", [])]
    sector_funds[name] = codes
    for f in sector.get("funds", []):
        sector_alias[f["code"]] = f.get("alias", "")

all_codes = list(dict.fromkeys([c for codes in sector_funds.values() for c in codes]))
results_list = calculate_valuation_batch(all_codes)
results = {r["fund_code"]: r for r in results_list}

output = {}
for sector, codes in sector_funds.items():
    sector_results = []
    changes = []
    for code in codes:
        r = results.get(code, {})
        change = r.get("estimation_change")
        if change is not None:
            changes.append(change)
        sector_results.append({
            "code": code,
            "name": r.get("fund_name", sector_alias.get(code, code)),
            "change": change,
            "week_change": r.get("week_change"),
            "source": r.get("_source"),
            "confidence": r.get("calibrated_confidence"),
        })
    avg = round(sum(changes) / len(changes), 2) if changes else None
    output[sector] = {"avg_change": avg, "funds": sector_results}

with open("data/today_valuation.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print("DONE")
