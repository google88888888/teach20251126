import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from openai import OpenAI

# 初始化 OpenAI 客户端
client = OpenAI(
    base_url='https://api.siliconflow.cn/v1/',
    api_key=''
)

st.title("现金流量表分析 💸")

# 从session state获取数据
if 'cash_flow_df' not in st.session_state:
    st.error("请先在主页加载数据")
    st.stop()

cash_flow_df = st.session_state.cash_flow_df

# 筛选年报数据
cash_flow_10 = cash_flow_df[
    cash_flow_df['报告日'].str.endswith('1231')
].head(10).iloc[::-1]
cash_flow_10['报告日'] = cash_flow_10['报告日'].str[:4]

legend=dict(
    title=None,
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
)

def plot_cash_flow_comparison(activity_type):
    """
    绘制现金流入流出对比图
    
    参数:
    activity_type: str, 活动类型，如'经营活动'、'投资活动'或'筹资活动'

    返回:
    fig: plotly图表对象
    """
    # 创建子图
    fig = make_subplots(rows=1, cols=2, column_widths=[0.75, 0.25], horizontal_spacing=0.05)
    
    # 添加现金流入小计柱状图
    inflow_col = f'{activity_type}现金流入小计'
    fig.add_trace(go.Bar(
        y=cash_flow_10['报告日'],
        x=cash_flow_10[inflow_col] / 100000000,
        name=inflow_col,
        orientation='h',
        text=[f'{x:.2f}' for x in cash_flow_10[inflow_col] / 100000000],
        textposition='auto'
    ), row=1, col=1)
    
    # 添加现金流出小计柱状图
    outflow_col = f'{activity_type}现金流出小计'
    fig.add_trace(go.Bar(
        y=cash_flow_10['报告日'], 
        x=-cash_flow_10[outflow_col] / 100000000,
        name=outflow_col,
        orientation='h',
        text=[f'{x:.2f}' for x in cash_flow_10[outflow_col] / 100000000],
        textposition='auto'
    ), row=1, col=1)
    
    # 添加现金流量净额折线图
    net_col = f'{activity_type}产生的现金流量净额'
    fig.add_trace(go.Scatter(
        y=cash_flow_10['报告日'],
        x=cash_flow_10[net_col] / 100000000,
        name=net_col,
        mode='lines+markers+text',
        text=[f'{x:.2f}' for x in cash_flow_10[net_col] / 100000000],
        textposition='middle left',
        yaxis='y2'
    ), row=1, col=2)
    
    # 更新布局
    fig.update_layout(
        title=f'{activity_type}现金流入流出对比',
        height=600,
        yaxis2=dict(side='right'),
        legend=legend,
        barmode='relative'
    )
    
    # 更新x轴和y轴标题
    fig.update_xaxes(title_text="金额（亿元）", row=1, col=1)
    fig.update_xaxes(title_text="金额（亿元）", row=1, col=2)
    fig.update_yaxes(title_text="年份", row=1, col=1)
    
    fig.update_traces(cliponaxis=False)  # 允许文本显示在绘图区域之外
    
    return fig

# 修改Tab顺序，将净额对比放在第一位
tab0, tab1, tab2, tab3 = st.tabs(["净额对比 📊", "经营活动 💼", "投资活动 💰", "筹资活动 🏦"])

with tab0:
    # 创建三项现金流量净额对比图
    # 准备数据
    cash_flow_plot = cash_flow_10.copy()
    cash_flow_plot[['经营活动产生的现金流量净额', '投资活动产生的现金流量净额', '筹资活动产生的现金流量净额']] = cash_flow_plot[['经营活动产生的现金流量净额', '投资活动产生的现金流量净额', '筹资活动产生的现金流量净额']].astype(float) / 100000000

    # 使用plotly express绘制分组柱状图
    fig = px.bar(
        cash_flow_plot,
        x='报告日',
        y=['经营活动产生的现金流量净额', '投资活动产生的现金流量净额', '筹资活动产生的现金流量净额'],
        text_auto='.2f',
        barmode='group',
        title='三大活动现金流量净额趋势对比',
        height=600
    )

    # 更新布局
    fig.update_layout(
        legend=legend,
        xaxis_title='年份',
        yaxis_title='金额（亿元）',
    )

    # 添加数值标签
    fig.update_traces(
        textposition='outside'
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("智能财务分析 🤖")

    # 初始化 session state 用于存储分析结果
    if "cash_flow_analysis" not in st.session_state:
        st.session_state.cash_flow_analysis = None

    if st.button("生成现金流分析报告") or st.session_state.cash_flow_analysis:
        if not st.session_state.cash_flow_analysis:  # 如果没有缓存的分析结果，则生成新的
            # 准备现金流数据字符串
            cash_flow_data = cash_flow_10[['报告日','经营活动产生的现金流量净额','投资活动产生的现金流量净额','筹资活动产生的现金流量净额']]
            cash_flow_data[['经营活动产生的现金流量净额','投资活动产生的现金流量净额','筹资活动产生的现金流量净额']]=cash_flow_data[['经营活动产生的现金流量净额','投资活动产生的现金流量净额','筹资活动产生的现金流量净额']]/100000000            
            cash_flow_data = cash_flow_data.to_markdown()

            # 创建分析请求
            messages = [
                {"role": "system", "content": "你是一个专业的财务分析师，请根据提供的现金流数据进行专业的分析，包括现金流结构、趋势、经营质量等方面。在分析中加入适当的emoji表情增强可读性。"},
                {"role": "user", "content": f"请分析以下现金流数据，给出专业的见解，数据单位是亿元：\n{cash_flow_data}"}
            ]

            # 调用 DeepSeek API
            response = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",
                messages=messages,
                stream=True,
            )

            # 定义完整思考过程和回复内容
            reasoning_content = ""
            answer_content = ""
            is_answering = False

            response_placeholder = st.empty()
            answer_placeholder = st.empty()

            # 使用加载状态组件显示思考过程
            with response_placeholder.container():
                with st.status("🤔 正在分析现金流数据...", expanded=True) as status:
                    thinking_placeholder = st.empty()
                    
                    for chunk in response:
                        # 获取思考过程
                        if chunk.choices[0].delta.reasoning_content:
                            reasoning_content += chunk.choices[0].delta.reasoning_content
                            thinking_placeholder.markdown(reasoning_content)
                        
                        # 获取回答内容
                        if chunk.choices[0].delta.content:
                            if not is_answering:
                                status.update(label="✨ 分析完成！", state="complete")
                                is_answering = True
                            answer_content += chunk.choices[0].delta.content
                            answer_placeholder.markdown(answer_content)

                # 更新 session state 用于存储分析结果
                st.session_state.cash_flow_analysis = answer_content
                
        else:  # 如果有缓存的分析结果，直接显示
            st.markdown(st.session_state.cash_flow_analysis)

        # 添加清除分析结果的按钮
        if st.button("清除分析结果"):
            st.session_state.cash_flow_analysis = None
            st.rerun()

with tab1:
    # 调用函数绘制经营活动现金流入流出对比图
    fig = plot_cash_flow_comparison(activity_type='经营活动')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # 调用函数绘制投资活动现金流入流出对比图
    fig = plot_cash_flow_comparison(activity_type='投资活动')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    # 调用函数绘制筹资活动现金流入流出对比图
    fig = plot_cash_flow_comparison(activity_type='筹资活动')    
    st.plotly_chart(fig, use_container_width=True) 