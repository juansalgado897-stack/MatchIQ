from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='MatchIQ 3.0', page_icon='⚽', layout='wide')
st.title('⚽ MatchIQ | The Story Behind the Game')
st.caption('Synthetic football data • Evidence-first insights • Optional Microsoft Foundry AI')
path = Path(__file__).parent / 'data' / 'synthetic_match.csv'
if not path.exists():
    st.error('Run `python generate_data.py` to create synthetic data.')
    st.stop()
df = pd.read_csv(path).sort_values(['minute','second','event_id'])
team_names = list(df.team.unique())
minute = st.slider('Match minute', 1, 90, 90)
view = df[df.minute <= minute].copy()
counts = view.team.value_counts().reindex(team_names, fill_value=0)
shots = view[view.event_type == 'shot']
xg = shots.groupby('team').xg.sum().reindex(team_names, fill_value=0)
a,b,c = st.columns(3)
a.metric(f'{team_names[0]} event share (not possession)', f'{counts.iloc[0]/len(view):.0%}')
b.metric('Shots (home / away)', f'{(shots.team==team_names[0]).sum()} / {(shots.team==team_names[1]).sum()}')
c.metric('Synthetic xG (home / away)', f'{xg.iloc[0]:.2f} / {xg.iloc[1]:.2f}')
st.caption('Event share is not ball possession. xG is randomly simulated, not estimated from a trained model.')
activity = view.assign(window=((view.minute-1)//5)*5+1).groupby(['window','team']).size().reset_index(name='events')
st.plotly_chart(px.line(activity,x='window',y='events',color='team',markers=True,title='Recorded event activity by 5-minute window'),use_container_width=True)

st.header('🔎 Turning Point Detector')
st.caption('Compares consecutive 15-minute windows. A shift means a change in logged event share, not proof of tactical intent.')
window = 15
records = []
for boundary in range(2*window, minute+1, 5):
    previous = view[(view.minute > boundary-2*window) & (view.minute <= boundary-window)]
    recent = view[(view.minute > boundary-window) & (view.minute <= boundary)]
    if not len(previous) or not len(recent):
        continue
    for team in team_names:
        old = int((previous.team==team).sum()); new = int((recent.team==team).sum())
        old_share = old/len(previous); new_share = new/len(recent)
        old_shots = int(((previous.team==team)&(previous.event_type=='shot')).sum())
        new_shots = int(((recent.team==team)&(recent.event_type=='shot')).sum())
        records.append({'team':team,'boundary':boundary,'previous_range':f'{boundary-2*window+1}–{boundary-window}', 'recent_range':f'{boundary-window+1}–{boundary}', 'old':old,'new':new,'old_total':len(previous),'new_total':len(recent),'old_share':old_share,'new_share':new_share,'change_pp':(new_share-old_share)*100,'old_shots':old_shots,'new_shots':new_shots})
if records:
    shifts = pd.DataFrame(records)
    winner = shifts.loc[shifts.change_pp.idxmax()]
    if winner.change_pp <= 0:
        st.info('No positive activity-share shift detected yet.')
    else:
        st.metric('Largest positive event-share shift',f'{winner.team}',f'+{winner.change_pp:.1f} percentage points')
        st.write(f"**Comparison:** minutes {winner.previous_range} vs {winner.recent_range}. Event share changed from **{winner.old_share:.0%}** ({int(winner.old)}/{int(winner.old_total)}) to **{winner.new_share:.0%}** ({int(winner.new)}/{int(winner.new_total)}). Shots: **{int(winner.old_shots)} → {int(winner.new_shots)}**.")
        audience = st.radio('Narrative audience', ['Fan','Broadcaster','Analyst'],horizontal=True)
        if audience == 'Fan':
            narrative = f"Something changed for {winner.team}! Their share of recorded match events rose by {winner.change_pp:.1f} percentage points in the next 15-minute period. That's a noticeable activity shift—not necessarily more possession."
        elif audience == 'Broadcaster':
            narrative = f"Keep an eye on {winner.team}: between minutes {winner.recent_range}, they accounted for {winner.new_share:.0%} of recorded events, up from {winner.old_share:.0%} in the preceding 15 minutes. Their shot count changed from {int(winner.old_shots)} to {int(winner.new_shots)}."
        else:
            narrative = f"The event-share differential for {winner.team} is +{winner.change_pp:.1f} percentage points across adjacent 15-minute windows ({winner.previous_range} vs {winner.recent_range}). Logged shots changed {int(winner.old_shots)}→{int(winner.new_shots)}. This is descriptive evidence, not causal proof of a tactical adjustment."
        st.info(narrative)
        with st.expander('Evidence: underlying events for these windows'):
            evidence = view[(view.minute > int(winner.boundary)-30)&(view.minute <= int(winner.boundary))]
            st.dataframe(evidence[['event_id','minute','second','team','event_type','xg']],use_container_width=True)
    with st.expander('All evaluated windows'):
        st.dataframe(shifts[['team','previous_range','recent_range','old_share','new_share','change_pp','old_shots','new_shots']],use_container_width=True)
else:
    st.info('Move the minute slider to 30 or later to detect a shift.')

st.header('Ask the Match — verified questions')
question = st.selectbox('Choose a question',['Which team has more shots?','Which team has higher synthetic xG?','Which team has more logged events?'])
if question.startswith('Which team has more shots'):
    vals = shots.team.value_counts().reindex(team_names,fill_value=0)
    answer = f'{vals.idxmax()} leads shots, {vals.max()} to {vals.min()}.' if vals.iloc[0]!=vals.iloc[1] else f'Tied at {vals.iloc[0]} shots each.'
elif 'xG' in question:
    answer = f'{xg.idxmax()} has higher simulated xG ({xg.max():.2f} vs {xg.min():.2f}).' if xg.iloc[0]!=xg.iloc[1] else 'Synthetic xG is tied.'
else:
    answer = f'{counts.idxmax()} has more recorded events ({counts.max()} vs {counts.min()}).' if counts.iloc[0]!=counts.iloc[1] else 'Recorded events are tied.'
st.success(answer)
st.caption('Verified questions use deterministic calculations, not generative AI.')


st.header('🤖 MatchIQ AI Studio — optional Microsoft Foundry')
st.caption('The assistant receives only the current synthetic-match summary. It must not claim tactical causes, real possession, or real Premier League data.')
with st.expander('Connection settings (optional; do not share keys)'):
    st.write('If you do not have an Azure deployment yet, leave these fields blank. The original MatchIQ features will continue to work.')
    endpoint = st.text_input('Azure OpenAI / Foundry model endpoint (base URL ending in /openai/v1/)', value='', placeholder='https://YOUR-RESOURCE.openai.azure.com/openai/v1/')
    deployment = st.text_input('Deployment name', value='', placeholder='Your deployed model name')
    api_key = st.text_input('API key', value='', type='password')
    st.caption('These inputs are for local testing. Never put API keys in GitHub or screenshots. Confirm the endpoint and deployment in your Azure portal.')

ai_audience = st.selectbox('AI narrative audience', ['Fan', 'Broadcaster', 'Analyst'], key='ai_audience')
ai_question = st.text_area('Ask about the synthetic match', value='What changed in match activity, and what can we actually conclude?', height=85)

summary = {
    'minute': int(minute),
    'teams': team_names,
    'recorded_events': {t: int(counts.loc[t]) for t in team_names},
    'shots': {t: int((shots.team == t).sum()) for t in team_names},
    'simulated_xg': {t: round(float(xg.loc[t]), 3) for t in team_names},
    'largest_positive_event_share_shift': None,
}
if records and winner.change_pp > 0:
    summary['largest_positive_event_share_shift'] = {
        'team': str(winner.team),
        'previous_minutes': str(winner.previous_range),
        'recent_minutes': str(winner.recent_range),
        'previous_event_share': round(float(winner.old_share), 4),
        'recent_event_share': round(float(winner.new_share), 4),
        'change_percentage_points': round(float(winner.change_pp), 2),
        'shots_previous': int(winner.old_shots),
        'shots_recent': int(winner.new_shots),
    }

if st.button('Generate AI explanation', type='primary'):
    if not all([endpoint.strip(), deployment.strip(), api_key.strip()]):
        st.warning('AI is not connected yet. Enter your Azure endpoint, deployment name and API key after activating an eligible Azure resource.')
        st.json(summary)
    elif not endpoint.startswith('https://') or not endpoint.rstrip('/').endswith('/openai/v1'):
        st.error('Use an HTTPS Azure OpenAI-compatible v1 endpoint ending in /openai/v1/.')
    else:
        try:
            from openai import OpenAI
            import json
            client = OpenAI(base_url=endpoint.rstrip('/') + '/', api_key=api_key, timeout=25.0, max_retries=0)
            instruction = (
                'You are MatchIQ, an evidence-grounded football match explainer. '
                'Use ONLY the supplied synthetic data. Never invent match events, player names, goals, '
                'tactical adjustments, causes, real possession, or trained xG predictions. '
                'Explicitly distinguish recorded-event share from ball possession. '
                'The simulated xG is not a trained estimate. If the question cannot be answered '
                'from the summary, say so. Write in English, concise and clear. '
                'Use the requested audience style and include specific numbers as evidence.'
            )
            payload = json.dumps({'audience': ai_audience, 'question': ai_question, 'match_summary': summary})
            with st.spinner('Generating an evidence-grounded explanation...'):
                response = client.chat.completions.create(
                    model=deployment.strip(),
                    messages=[{'role': 'system', 'content': instruction}, {'role': 'user', 'content': payload}],
                    temperature=0.2,
                )
            st.success('AI-generated narrative (verify against the evidence below)')
            st.write(response.choices[0].message.content or 'No text returned.')
            with st.expander('Evidence sent to the model'):
                st.json(summary)
        except ImportError:
            st.error('Missing dependency. In your active virtual environment run: python -m pip install openai')
        except Exception as exc:
            st.error('AI connection failed. Check the endpoint, deployment, key, permissions, and Azure quota.')
            st.caption(f'Error type: {type(exc).__name__}. For security, full error details are not displayed.')
