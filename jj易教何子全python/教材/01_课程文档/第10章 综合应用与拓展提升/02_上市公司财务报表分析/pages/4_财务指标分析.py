import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("财务指标分析 📊")

# 从session state获取数据
if 'financial_indicators_df' not in st.session_state:
    st.error("请先在主页加载数据")
    st.stop()

fin_indicator_df = st.session_state.financial_indicators_df

# 筛选年报数据
annual_data = fin_indicator_df[fin_indicator_df['日期'].str.endswith('12-31')].tail(10)
annual_data['日期'] = annual_data['日期'].str[:4]

legend=dict(
    title=None,
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
)

# 定义绘图函数
def plot_financial_indicator(y_column, title=None):
    """
    绘制财务指标趋势图
    
    参数:
    y_column: 要绘制的指标列名
    title: 图表标题，如果不提供则使用指标名称
    """
    # 创建图表
    fig = go.Figure()
    
    # 添加指标曲线
    fig.add_trace(go.Scatter(
        x=annual_data['日期'],
        y=annual_data[y_column],
        mode='lines+markers+text',
        text=[f'{x:.2f}' for x in annual_data[y_column]],
        textposition='top center'
    ))
    
    # 更新布局
    fig.update_layout(
        title=title if title else f'{y_column}趋势分析',
        xaxis_title='年份',
        yaxis_title='周转率(次)',
    )
    
    # 显示图表
    return fig

# 创建Tab组件，调整顺序
tab1, tab2, tab3, tab4 = st.tabs(["营运能力 🔄", "盈利能力 💹", "偿债能力 💪", "发展能力 📈"])

with tab1:
    st.subheader("营运能力指标趋势")

    # 绘制总资产周转率图表
    fig1 = plot_financial_indicator('总资产周转率(次)', '总资产周转率趋势分析')
    st.plotly_chart(fig1, use_container_width=True)

    # 创建两列布局
    col1, col2 = st.columns(2)

    # 应收账款周转率图表
    with col1:
        fig2 = plot_financial_indicator('应收账款周转率(次)', '应收账款周转率趋势分析')
        st.plotly_chart(fig2, use_container_width=True)

    # 存货周转率图表
    with col2:
        fig3 = plot_financial_indicator('存货周转率(次)', '存货周转率趋势分析')
        st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("盈利能力指标趋势")
    
    # 使用plotly express创建图表
    fig = px.line(
        annual_data, 
        x='日期', 
        y=['净资产收益率(%)', '总资产利润率(%)', '销售净利率(%)'],
        markers=True,
        title='盈利能力指标趋势分析'
    )

    # 美化图表
    fig.update_layout(
        xaxis_title='年份',
        yaxis_title='百分比(%)',
        legend=legend
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("长期偿债能力指标趋势")
    
    # 绘制资产负债率图表
    fig0 = plot_financial_indicator('资产负债率(%)', '资产负债率趋势分析')
    st.plotly_chart(fig0, use_container_width=True)
    
    st.subheader("短期偿债能力指标趋势")
    col1, col2 = st.columns(2)
    
    with col1:
        # 流动比率趋势图
        fig1 = plot_financial_indicator('流动比率', '流动比率趋势分析')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # 速动比率趋势图
        fig2 = plot_financial_indicator('速动比率', '速动比率趋势分析')
        st.plotly_chart(fig2, use_container_width=True)
    
    # 现金比率趋势图
    fig3 = plot_financial_indicator('现金比率(%)', '现金比率趋势分析')
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("发展能力指标趋势")
    
    # 从利润表中获取营业收入和净利润数据
    profit_sheet_10 = st.session_state.profit_sheet_df[
        st.session_state.profit_sheet_df['报告日'].str.endswith('1231')
    ].head(10).iloc[::-1]
    profit_sheet_10['报告日'] = profit_sheet_10['报告日'].str[:4]

    # 计算营业收入增长率和净利润增长率
    profit_sheet_10['营业收入增长率'] = profit_sheet_10['营业收入'].pct_change() * 100
    profit_sheet_10['净利润增长率'] = profit_sheet_10['净利润'].pct_change() * 100

    # 第一个图：收入与利润增长率趋势图
    # 使用plotly express创建折线图
    fig = px.line(
        profit_sheet_10, 
        x='报告日', 
        y=['营业收入增长率', '净利润增长率'],
        markers=True,
        title='收入与利润增长率趋势分析',
    )

    # 更新布局
    fig.update_layout(
        xaxis_title='报告期',
        yaxis_title='增长率(%)',
        legend=legend
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 第二个图：资产增长率趋势图
    # 使用plotly express创建折线图
    fig = px.line(
        annual_data, 
        x='日期', 
        y=['净资产增长率(%)', '总资产增长率(%)'],
        markers=True,
        title='资产增长率趋势分析',
    )

    # 更新布局
    fig.update_layout(
        xaxis_title='报告期',
        yaxis_title='增长率(%)',
        legend=legend
    )
    
    st.plotly_chart(fig, use_container_width=True) 