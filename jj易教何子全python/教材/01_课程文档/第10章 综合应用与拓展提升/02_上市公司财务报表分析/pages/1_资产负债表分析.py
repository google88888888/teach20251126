import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.title("资产负债表分析 📈")

# 从session state获取数据
if 'balance_sheet_df' not in st.session_state:
    st.error("请先在主页加载数据")
    st.stop()

balance_sheet_df = st.session_state.balance_sheet_df

# 筛选年报数据
balance_sheet_10 = balance_sheet_df[
    balance_sheet_df['报告日'].str.endswith('1231')
].head(10).iloc[::-1]
balance_sheet_10['报告日'] = balance_sheet_10['报告日'].str[:4]

legend=dict(
    title=None,
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("资产结构分析")

    # 准备数据
    df_assets = pd.DataFrame({
        '报告日': balance_sheet_10['报告日'],
        '流动资产': balance_sheet_10['流动资产合计']/100000000,
        '非流动资产': balance_sheet_10['非流动资产合计']/100000000,
    })

    # 创建资产结构堆积面积图
    fig1 = px.area(df_assets, 
        x='报告日',
        y=['流动资产', '非流动资产'],
        title='资产结构分析'
    )

    # 更新布局
    fig1.update_layout(
        xaxis_title='报告期',
        yaxis_title='金额（亿元）',
        legend=legend
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
with col2:
    st.subheader("负债结构分析")

    # 准备数据
    df_liabilities = pd.DataFrame({
        '报告日': balance_sheet_10['报告日'],
        '流动负债': balance_sheet_10['流动负债合计']/100000000,
        '非流动负债': balance_sheet_10['非流动负债合计']/100000000,
    })

    # 创建负债结构堆积面积图
    fig2 = px.area(df_liabilities,
        x='报告日',
        y=['流动负债', '非流动负债'],
        title='负债结构分析'
    )

    # 更新布局
    fig2.update_layout(
        xaxis_title='报告期',
        yaxis_title='金额（亿元）',
        legend=legend
    )
    
    st.plotly_chart(fig2, use_container_width=True)

# 在两列布局后添加新的图表
st.subheader("负债和所有者权益结构分析")

# 准备数据
df_liabilities_equity = pd.DataFrame({
    '报告日': balance_sheet_10['报告日'],
    '负债合计': balance_sheet_10['负债合计']/100000000,
    '所有者权益合计': balance_sheet_10['所有者权益(或股东权益)合计']/100000000
})

df_liabilities_equity[['负债合计', '所有者权益合计']] = df_liabilities_equity[['负债合计', '所有者权益合计']].astype(float)

# 创建堆叠柱状图
fig3 = px.bar(df_liabilities_equity,
    x='报告日',
    y=['负债合计', '所有者权益合计'],
    title='负债和所有者权益结构分析', 
    text_auto='.2f'
)

# 更新布局
fig3.update_layout(
    xaxis_title='报告期',
    yaxis_title='金额（亿元）',
    legend=legend
)

st.plotly_chart(fig3, use_container_width=True) 