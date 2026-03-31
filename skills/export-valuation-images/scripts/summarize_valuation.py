import json

with open('data/today_valuation.json', encoding='utf-8') as f:
    data = json.load(f)

lines = []
for sector, info in data.items():
    avg = info['avg_change']
    fund_count = len(info['funds'])
    sign = '+' if avg and avg > 0 else ''
    sorted_funds = sorted(info['funds'], key=lambda x: x['change'] if x['change'] is not None else 0, reverse=True)
    top = sorted_funds[0] if sorted_funds else None
    bot = sorted_funds[-1] if sorted_funds else None

    def fmt(f):
        if f and f['change'] is not None:
            s = '+' if f['change'] > 0 else ''
            return f"{f['name']}({s}{f['change']}%)"
        return '-'

    lines.append(f"{sector}({fund_count}只): 均{sign}{avg}% | 最强: {fmt(top)} | 最弱: {fmt(bot)}")

print('\n'.join(lines))
