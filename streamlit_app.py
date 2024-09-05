import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

validator_uids = [133,2,6,0,4,3,74,299,147,123,1,118]

st.set_page_config(page_title="LogicNet Studio", layout="wide")

st.markdown("<h1 style='text-align: center;'>LogicNet Statistics</h1>", unsafe_allow_html=True)
st.markdown(
    """
    <p style='text-align: center;'>LogicNet is a Bittensor-powered network that drives the development of AI models capable of complex 
    mathematical problem-solving and detailed data analysis. Below, you will find statistics of the network, 
    its performance, and comparisons to other models.</p>
    """,
    unsafe_allow_html=True
)

data = {
    "Model": ["Llama 2", "Code Llama", "LogicNet", "Minerva", "", "Code Llama", "", "Minerva", "Minerva"],
    "Size": ["7B", "7B", "7B", "8B", "", "34B", "", "62B", "540B"],
    "GSM8k": ["11.8%", "10.5%", "36.4%", "16.2%", "", "29.6%", "", "52.4%", "58.8%"],
    "OCW": ["3.7%", "4.4%", "7.7%", "7.7%", "", "7.0%", "", "12.0%", "17.6%"],
    "MMLU-STEM": ["29.9%", "25.1%", "37.7%", "35.6%", "", "40.5%", "", "53.9%", "63.9%"],
    "SAT": ["25%", "9.4%", "53.1%", "-", "", "40.6%", "", "-", "-"],
    "MATH": ["3.2%", "4.5%", "18.0%", "14.1%", "", "12.2%", "", "27.6%", "33.6%"]
}

# Convert the dictionary to a DataFrame
df = pd.DataFrame(data)

# Display the DataFrame as a table in Streamlit
st.table(df)
st.markdown(
    """
    <p style='text-align: center;'>Figure 1: Comparison of LogicNet and other models on well-established benchmarks.</p>
    """, 
    unsafe_allow_html=True
)


validator_select = st.selectbox(
        "Select a validator",
        validator_uids,
        index=validator_uids.index(133)
)
validator_select = str(validator_select)

if f"stats" not in st.session_state:
    response = requests.get("https://logicnet.aitprotocol.ai/proxy_client/get_miner_information")
    response = response.json()
    st.session_state.stats = response

if f"timeline_stats" not in st.session_state:
    response_timeline = requests.get("https://logicnet.aitprotocol.ai/proxy_client/get_miner_statistics")
    response_timeline = response_timeline.json()
    st.session_state.timeline_stats = response_timeline
response = st.session_state.stats[validator_select]

if validator_select in st.session_state.timeline_stats:
    response_timeline = st.session_state.timeline_stats[validator_select]

    ### Plot acc of top miner chart
    df = pd.DataFrame(response_timeline["average_top_accuracy"])
    df['updated_time'] = df['updated_time'].apply(lambda x: datetime.utcfromtimestamp(x).replace(second=0, microsecond=0))

    fig = px.line(df, x='updated_time', y='mean_accuracy', title='Average Accuracy', markers=True)

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Accuracy',
        hovermode='x',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='LightGrey', range=[0, 1]),
    )
    st.plotly_chart(fig)


category_distribution = {}
for uid, info in response["miner_information"].items():
    category = info["category"]
    category_distribution[category] = category_distribution.get(category, 0) + 1

fig = px.pie(
    values=list(category_distribution.values()),
    names=list(category_distribution.keys()),
    title="Category Distribution",
)
st.plotly_chart(fig)

transformed_dict = []
for k, v in response['miner_information'].items():
    transformed_dict.append(
        {
            "uid": k,
            "category": v["category"],
            "mean_score": (
                sum(v["scores"]) / 10
            ),
            "epoch_volume": v["epoch_volume"],
        }
    )
transformed_dict = pd.DataFrame(transformed_dict)

for category in category_distribution.keys():
    if not category:
        continue
    category_data = transformed_dict[transformed_dict["category"] == category]
    category_data = category_data.sort_values(by="mean_score", ascending=False)
    category_data.uid = category_data.uid.astype(str)
    if category_data.mean_score.sum() == 0:
        continue
    fig = go.Figure(data=[go.Bar(x=category_data.uid, y=category_data.mean_score,
            hovertext=[f"Epoch volume: {volume}" for volume in category_data.epoch_volume], marker_color='lightsalmon')])
    fig.update_layout(title_text=f"category: {category}", xaxis_title="UID", yaxis_title="Mean Score")
    
    fig.update_layout(
        xaxis=dict(type="category"),
    )
    st.plotly_chart(fig)

for uid, info in response["miner_information"].items():
    info["accuracy"] = [x["correctness"] for x in info.get("reward_logs",[])]
    info.pop("reward_logs", None)
pd_data = pd.DataFrame(response["miner_information"])

st.markdown(
    """
    **Total Information**
    """,
    unsafe_allow_html=True,
)
st.dataframe(pd_data.T,
    width=1500,
    column_order = ("category", "scores", "epoch_volume", "accuracy", "reward_scale", "rate_limit"),
    column_config = {
        "scores": st.column_config.ListColumn(
            "Scores",
            width ="large"
        ),
        "category": st.column_config.TextColumn(
            "Category"
        ),
        "epoch_volume": st.column_config.ProgressColumn(
            "Volume",
            format="%f",
            min_value=0,
            max_value=512,
        ),
        "reward_scale": st.column_config.NumberColumn(
            "Reward Scale"
        ),
        "accuracy": st.column_config.ListColumn(
            "Accuracy",
            width ="large"
        ),
        "rate_limit": st.column_config.NumberColumn(
            "Rate Limit"
        )
    })

