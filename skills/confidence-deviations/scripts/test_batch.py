import sys
sys.path.insert(0, '.')
from valuation.core import load_state

state = load_state()
print('Sector count:', len(state.get('sectors', [])))
for s in state.get('sectors', []):
    fund_count = len(s.get('funds', []))
    print(f"- {s['name']}: {fund_count} funds")
