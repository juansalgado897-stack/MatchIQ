# MatchIQ — The Story Behind the Game

Early working prototype for the Inside the Game hackathon.

## Run locally

```bash
pip install -r requirements.txt
python generate_data.py
streamlit run app.py
```

## Data integrity

All events, teams, coordinates and xG values are generated synthetically. The xG field is a random simulated value and is not a calibrated expected-goals model. The event share shown as a possession proxy is **not** time-based possession. This project does not include real Premier League match data.

## Implemented

- Reproducible synthetic event generator
- Time-window event activity visualization
- Shot and simulated xG summaries
- Rule-based explanations with traceable underlying event data

## Planned (not yet implemented)

- Microsoft Foundry integration with grounded narrative generation
- Structured event validation and stronger football-realistic simulation
- Multi-agent pipeline with fact-checking
- Automated recap and demo deployment
