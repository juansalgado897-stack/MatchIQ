import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path(__file__).parent / 'data'
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(27)
teams = ['Harbor City FC', 'Northbridge United']
rows = []
for minute in range(1, 91):
    n = int(rng.integers(3, 7))
    for j in range(n):
        team = teams[int(rng.choice([0, 1], p=[0.54 if minute < 55 else 0.43, 0.46 if minute < 55 else 0.57]))]
        kind = str(rng.choice(['pass','carry','tackle','interception','shot','foul'], p=[0.53,0.19,0.12,0.08,0.055,0.025]))
        x, y = float(rng.uniform(0,100)), float(rng.uniform(0,100))
        xg = round(float(rng.uniform(0.02, 0.35)), 3) if kind == 'shot' else 0.0
        rows.append({'event_id':len(rows)+1,'minute':minute,'second':int(rng.integers(0,60)), 'team':team,'event_type':kind,'x':round(x,1),'y':round(y,1),'xg':xg})
df = pd.DataFrame(rows).sort_values(['minute','second','event_id']).reset_index(drop=True)
df.to_csv(OUT / 'synthetic_match.csv', index=False)
print(f'Generated {len(df)} fully synthetic events: {OUT / "synthetic_match.csv"}')
