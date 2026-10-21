from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='MatchIQ 4.0 | The Story Behind the Game', page_icon='⚽', layout='wide')
st.markdown('''<style>
.block-container {padding-top: 1.7rem; max-width: 1280px}
.hero {padding: 24px 28px; border-radius: 18px; background: linear-gradient(120deg,#102d3a,#164b54);color:white;margin-bottom:16px}
.hero h1 {color:white;font-size:2.4rem;margin:0}
.hero p {color:#cbe5e4;margin:9px 0 0}
.pill {display:inline-block;padding:4px 11px;border-radius:18px;background:#def6ee;color:#145542;font-size:.8rem;font-weight:700}
.note {padding:12px 16px;border-left:4px solid #1b9386;background:#eaf7f5;border-radius:6px;color:#174e49}
</style>''', unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="pill">MATCHIQ 4.0 · SYNTHETIC MATCH INTELLIGENCE</div><h1>⚽ The Story Behind the Game</h1><p>From recorded events to explainable football stories · Evidence first · Optional Microsoft Foundry AI</p></div>', unsafe_allow_html=True)

path = Path(__file__).parent / 'data' / 'synthetic_match.csv'
if not path.exists():
    st.error('Match data not found. Run `python generate_data.py` to create `data/synthetic_match.csv`.')
    st.stop()
df = pd.read_csv(path).sort_values(['minute','second','event_id'])
needed = {'minute','second','event_id','team','event_type','xg'}
if not needed.issubset(df.columns):
    st.error('Missing expected columns: ' + ', '.join(sorted(needed-set(df.columns))))
    st.stop()
team_names = list(df['team'].dropna().unique())
if len(team_names) != 2:
    st.error('This prototype expects exactly two teams.')
    st.stop()

with st.sidebar:
    st.header('🎛️ Match controls')
    minute = st.slider('Match minute', 1, 90, 90)
    st.caption('Move the slider to explore the story as it unfolds.')
    st.divider()
    st.markdown('**Data integrity**')
    st.write('🟢 Synthetic match events')
    st.write('🟢 Deterministic verified metrics')
    st.write('🟡 Generative AI requires a configured model')
    st.caption('No real Premier League match data is used.')

view = df[df.minute <= minute].copy()
counts = view.team.value_counts().reindex(team_names,fill_value=0)
shots = view[view.event_type == 'shot']
shot_counts = shots.team.value_counts().reindex(team_names,fill_value=0)
xg = shots.groupby('team').xg.sum().reindex(team_names,fill_value=0)
share = counts / max(len(view),1)

st.subheader(f'🏟️ {team_names[0]}  vs  {team_names[1]}')
st.caption(f'Synthetic match · Through minute {minute} · No score or goals inferred from event counts')
c1,c2,c3,c4 = st.columns(4)
c1.metric('Logged events',f'{int(counts.iloc[0])} – {int(counts.iloc[1])}')
c2.metric('Shots',f'{int(shot_counts.iloc[0])} – {int(shot_counts.iloc[1])}')
c3.metric('Simulated xG',f'{xg.iloc[0]:.2f} – {xg.iloc[1]:.2f}')
c4.metric(f'{team_names[0]} event share',f'{share.iloc[0]:.0%}')
st.markdown('<div class="note">Event share ≠ ball possession. Simulated xG is randomly assigned, not produced by a trained xG model.</div>',unsafe_allow_html=True)

match_tab, turning_tab, question_tab, ai_tab = st.tabs(['📈 Match Center','🔎 Turning Points','💬 Ask the Match','🤖 AI Story Studio'])

with match_tab:
    st.subheader('Match activity timeline')
    activity = view.assign(window=((view.minute-1)//5)*5+1).groupby(['window','team']).size().reset_index(name='events')
    fig = px.line(activity,x='window',y='events',color='team',markers=True,color_discrete_sequence=['#0e827c','#ff755e'])
    fig.update_layout(xaxis_title='Five-minute window (starting minute)',yaxis_title='Recorded events',legend_title='',hovermode='x unified',margin=dict(l=10,r=10,t=20,b=10))
    st.plotly_chart(fig,use_container_width=True)
    a,b=st.columns(2)
    with a:
        st.subheader('Event share comparison')
        share_fig = go.Figure(go.Bar(x=team_names,y=[round(float(share.loc[t])*100,1) for t in team_names],marker_color=['#0e827c','#ff755e'],text=[f'{share.loc[t]:.0%}' for t in team_names],textposition='auto'))
        share_fig.update_layout(yaxis_title='% of recorded events',yaxis_range=[0,100],margin=dict(l=10,r=10,t=10,b=10),height=310)
        st.plotly_chart(share_fig,use_container_width=True)
    with b:
        st.subheader('Shot activity')
        shot_fig=px.bar(x=team_names,y=[int(shot_counts.loc[t]) for t in team_names],labels={'x':'Team','y':'Shots'},color=team_names,color_discrete_sequence=['#0e827c','#ff755e'])
        shot_fig.update_layout(showlegend=False,margin=dict(l=10,r=10,t=10,b=10),height=310)
        st.plotly_chart(shot_fig,use_container_width=True)
    with st.expander('Explore the synthetic event log'):
        st.dataframe(view[['event_id','minute','second','team','event_type','xg']],use_container_width=True,hide_index=True)

records=[]
window=15
for boundary in range(2*window,minute+1,5):
    prev=view[(view.minute>boundary-2*window)&(view.minute<=boundary-window)]
    recent=view[(view.minute>boundary-window)&(view.minute<=boundary)]
    if prev.empty or recent.empty:
        continue
    for team in team_names:
        old=int((prev.team==team).sum()); new=int((recent.team==team).sum())
        old_share=old/len(prev); new_share=new/len(recent)
        records.append(dict(team=team,boundary=boundary,previous_range=f'{boundary-29}–{boundary-15}',recent_range=f'{boundary-14}–{boundary}',old=old,new=new,old_total=len(prev),new_total=len(recent),old_share=old_share,new_share=new_share,change_pp=(new_share-old_share)*100,old_shots=int(((prev.team==team)&(prev.event_type=='shot')).sum()),new_shots=int(((recent.team==team)&(recent.event_type=='shot')).sum())))
shifts=pd.DataFrame(records)
winner=shifts.loc[shifts.change_pp.idxmax()] if not shifts.empty else None

with turning_tab:
    st.subheader('Largest observed positive event-share shift')
    st.caption('Method: adjacent 15-minute windows evaluated every five minutes. Descriptive, not causal.')
    if winner is None:
        st.info('Move the minute slider to 30 or later to see a detected shift.')
    elif winner.change_pp<=0:
        st.info('No positive shift detected in the evaluated windows.')
    else:
        m1,m2,m3=st.columns(3)
        m1.metric('Team',str(winner.team))
        m2.metric('Event-share change',f'+{winner.change_pp:.1f} pp')
        m3.metric('Shots, before → after',f'{int(winner.old_shots)} → {int(winner.new_shots)}')
        st.write(f'**Minutes {winner.previous_range} vs {winner.recent_range}:** {winner.old_share:.0%} ({int(winner.old)}/{int(winner.old_total)}) → {winner.new_share:.0%} ({int(winner.new)}/{int(winner.new_total)}) of logged events.')
        audience=st.segmented_control('Explain for',options=['Fan','Broadcaster','Analyst'],default='Fan',key='turning_audience')
        if audience=='Fan':
            narrative=f'📣 {winner.team} became more active in the event log! Its share rose by {winner.change_pp:.1f} percentage points across the two windows. That does not prove it had more possession.'
        elif audience=='Broadcaster':
            narrative=f'🎙️ Watch {winner.team}: it accounted for {winner.new_share:.0%} of recorded events in minutes {winner.recent_range}, up from {winner.old_share:.0%} in the prior window. Shots changed {int(winner.old_shots)} to {int(winner.new_shots)}.'
        else:
            narrative=f'📊 Descriptive change: {winner.team} recorded a +{winner.change_pp:.1f} pp event-share differential ({winner.previous_range} vs {winner.recent_range}); shots {int(winner.old_shots)}→{int(winner.new_shots)}. Neither causality nor tactical intent can be established.'
        st.info(narrative)
        st.caption('Rule-generated narrative · Not generative AI')
        with st.expander('🔍 Evidence: events behind this turning point'):
            evidence=view[(view.minute>int(winner.boundary)-30)&(view.minute<=int(winner.boundary))]
            st.dataframe(evidence[['event_id','minute','second','team','event_type','xg']],use_container_width=True,hide_index=True)
    with st.expander('Compare all evaluated windows'):
        if not shifts.empty:
            st.dataframe(shifts[['team','previous_range','recent_range','old_share','new_share','change_pp','old_shots','new_shots']],use_container_width=True,hide_index=True)

with question_tab:
    st.subheader('Verified questions')
    st.caption('Every answer below is calculated from the currently selected events, without a language model.')
    question=st.selectbox('Ask a question',['Which team has more shots?','Which team has higher synthetic xG?','Which team has more logged events?'])
    if 'more shots' in question:
        vals=shot_counts; unit='shots'
        answer=f'{vals.idxmax()} leads with {int(vals.max())} {unit} versus {int(vals.min())}.' if vals.iloc[0]!=vals.iloc[1] else f'Both teams have {int(vals.iloc[0])} shots.'
    elif 'xG' in question:
        vals=xg
        answer=f'{vals.idxmax()} leads in simulated xG: {vals.max():.2f} versus {vals.min():.2f}.' if vals.iloc[0]!=vals.iloc[1] else f'Both teams have {vals.iloc[0]:.2f} simulated xG.'
    else:
        vals=counts
        answer=f'{vals.idxmax()} has {int(vals.max())} logged events versus {int(vals.min())}.' if vals.iloc[0]!=vals.iloc[1] else f'Both teams have {int(vals.iloc[0])} logged events.'
    st.success(answer)
    st.caption(f'Based on {len(view)} recorded events through minute {minute}.')

summary={'minute':int(minute),'teams':team_names,'recorded_events':{t:int(counts.loc[t]) for t in team_names},'shots':{t:int(shot_counts.loc[t]) for t in team_names},'simulated_xg':{t:round(float(xg.loc[t]),3) for t in team_names},'largest_positive_event_share_shift':None}
if winner is not None and winner.change_pp>0:
    summary['largest_positive_event_share_shift']={'team':str(winner.team),'previous_minutes':str(winner.previous_range),'recent_minutes':str(winner.recent_range),'previous_event_share':round(float(winner.old_share),4),'recent_event_share':round(float(winner.new_share),4),'change_percentage_points':round(float(winner.change_pp),2),'shots_previous':int(winner.old_shots),'shots_recent':int(winner.new_shots)}

with ai_tab:
    st.subheader('AI Story Studio · Microsoft Foundry (optional)')
    st.caption('Generative explanations are available only after you connect a valid Azure-hosted model. The verified features work without Azure.')
    with st.expander('🔐 Connection settings — do not share keys'):
        endpoint=st.text_input('Azure OpenAI / Foundry v1 base endpoint',placeholder='https://YOUR-RESOURCE.openai.azure.com/openai/v1/')
        deployment=st.text_input('Model deployment name')
        api_key=st.text_input('API key',type='password')
        st.warning('For a public demo, do not enter private API keys in shared screens or recordings. For production, use server-side Streamlit secrets instead.')
    ai_audience=st.selectbox('Audience',['Fan','Broadcaster','Analyst'],key='ai_audience')
    ai_question=st.text_area('Question','What changed in match activity, and what can we actually conclude?',height=90)
    if st.button('Generate AI explanation',type='primary'):
        if not all([endpoint.strip(),deployment.strip(),api_key.strip()]):
            st.warning('AI is not connected yet. Configure a valid Azure endpoint, deployment and API key to generate a real AI explanation.')
            with st.expander('Evidence payload ready for a model'):
                st.json(summary)
        elif not endpoint.startswith('https://') or not endpoint.rstrip('/').endswith('/openai/v1'):
            st.error('The endpoint must be HTTPS and end with /openai/v1/.')
        else:
            try:
                from openai import OpenAI
                client=OpenAI(base_url=endpoint.rstrip('/')+'/',api_key=api_key,timeout=25.0,max_retries=0)
                instruction=('You are MatchIQ, an evidence-grounded football explainer. Use ONLY supplied synthetic match data. '
                             'Never invent goals, players, tactics, causes, ball possession, or real Premier League information. '
                             'Event share is not possession and simulated xG is not a trained prediction. '
                             'If the evidence does not answer the question, say so. Write in concise English, '
                             'adapt to the specified audience, and cite concrete supplied numbers.')
                payload=json.dumps({'audience':ai_audience,'question':ai_question,'match_summary':summary})
                with st.spinner('Generating grounded narrative...'):
                    response=client.chat.completions.create(model=deployment.strip(),messages=[{'role':'system','content':instruction},{'role':'user','content':payload}],temperature=0.2)
                st.success('AI-generated explanation — verify against the evidence')
                st.write(response.choices[0].message.content or 'No text returned.')
                with st.expander('Evidence sent to the model'):
                    st.json(summary)
            except ImportError:
                st.error('Missing package: add `openai` to requirements.txt and install it.')
            except Exception as exc:
                st.error('AI connection failed. Check your endpoint, deployment, key, permissions and quota.')
                st.caption(f'Error type: {type(exc).__name__}. Detailed error hidden for security.')

st.divider()
st.caption('MatchIQ 4.0 · Prototype for Inside the Game · Synthetic data only · No claims about real teams, scores, tactics, or possession')
