import streamlit as st
import requests
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

validator_uids = [3]


st.markdown(
    """
    **Logic Subnet: Artificial & Distributed Intelligent Brain.**
    Below is the statistics of the Logic Subnet.
    """,
    unsafe_allow_html=True,
)
validator_select = st.selectbox(
        "Select a validator",
        validator_uids,
        index=validator_uids.index(3)
)
validator_select = str(validator_select)

if f"stats" not in st.session_state:
    response = requests.get("https://logicnet.aitprotocol.ai/proxy_client/get_miner_information")
    response = response.json()
    st.session_state.stats = response

response = st.session_state.stats[validator_select]

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
pd_data = pd.DataFrame(response["miner_information"])

st.markdown(
    """
    **Total Information**
    """,
    unsafe_allow_html=True,
)
st.dataframe(pd_data.T)