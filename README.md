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

## Data and AI Transparency

MatchIQ is a prototype developed for the Inside the Game Developer Hackathon.

### Synthetic Data
- All teams and match events are fictional and synthetically generated.
- No real Premier League match data is used.
- Event share does not represent possession.
- Simulated xG values are not produced by a calibrated expected-goals model.
- Turning points describe changes in recorded activity, not tactical causality.

### AI Explainability
- Match statistics are calculated deterministically from the dataset.
- AI Story Studio uses Groq-powered generative AI to explain the supplied statistics.
- AI-generated narratives are interpretations, not independently verified facts.
- Core analytics remain available without an AI API key.

### Technology
- Python
- Streamlit
- pandas and NumPy
- Plotly
- Groq API (OpenAI-compatible interface)
- GitHub for version control and collaboration

### Live Demo
https://matchiq-football.streamlit.app/

### Video Demonstration
https://youtu.be/2oEPji3-vU0
