import streamlit as st
import pandas as pd
import altair as alt
from urllib.error import URLError

st.set_page_config(page_title="数据框演示", page_icon="📊")

st.markdown("# 数据框演示")
st.sidebar.header("数据框演示")
st.write(
    """本演示展示了如何使用 `st.write` 来可视化 Pandas 数据框。
(数据来源于 [UN Data Explorer](http://data.un.org/Explorer.aspx)。)"""
)


@st.cache_data
def get_UN_data():
    AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
    return df.set_index("Region")


try:
    df = get_UN_data()
    countries = st.multiselect(
        "选择国家", list(df.index), ["China", "United States of America"]
    )
    if not countries:
        st.error("请至少选择一个国家。")
    else:
        data = df.loc[countries]
        data /= 1000000.0
        st.write("### 农业总产值 (十亿美元)", data.sort_index())

        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "年份", "value": "农业总产值 (十亿美元)"}
        )
        chart = (
            alt.Chart(data)
            .mark_area(opacity=0.3)
            .encode(
                x="年份:T",
                y=alt.Y("农业总产值 (十亿美元):Q", stack=None),
                color="Region:N",
            )
        )
        st.altair_chart(chart, use_container_width=True)
except URLError as e:
    st.error(
        """
        **此演示需要互联网连接。**
        连接错误: %s
    """
        % e.reason
    )