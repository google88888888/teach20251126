import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

st.title("利润表分析 💰")

# 从session state获取数据
if 'profit_sheet_df' not in st.session_state:
    st.error("请先在主页加载数据")
    st.stop()

profit_sheet_df = st.session_state.profit_sheet_df

# 筛选年报数据
profit_sheet_10 = profit_sheet_df[
    profit_sheet_df['报告日'].str.endswith('1231')
].head(10).iloc[::-1]
profit_sheet_10['报告日'] = profit_sheet_10['报告日'].str[:4]

legend=dict(
    title=None,
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
)

# 创建Tab组件
tab1, tab2, tab3 = st.tabs(["利润构成 📊", "营业收入与成本 💰", "期间费用 💸"])

with tab1:
    st.subheader("利润构成分析")
    
    # 将选择器改为 segmented_control
    years = profit_sheet_10['报告日'].tolist()
    selected_year = st.selectbox(
        "选择年份",
        years,
        index=len(years)-1,
        format_func=lambda x: f"{x}年度",
        label_visibility="collapsed"
    )

    # 获取选中年份的数据
    waterfall_data = profit_sheet_10[profit_sheet_10['报告日'] == selected_year].iloc[0]

    # 计算毛利
    waterfall_data['毛利'] = waterfall_data['营业总收入'] - waterfall_data['营业成本']
    waterfall_data['营业利润'] = waterfall_data['毛利'] - waterfall_data['营业税金及附加'] - waterfall_data['研发费用'] - waterfall_data['销售费用'] - waterfall_data['管理费用'] - waterfall_data['财务费用']
    waterfall_data['利润总额'] = waterfall_data['营业利润'] + waterfall_data['营业外收入'] - waterfall_data['营业外支出']
    waterfall_data['净利润'] = waterfall_data['利润总额'] - waterfall_data['所得税费用']

    # 构建瀑布图数据
    measures = ['relative', 'relative', 'total', 'relative', 'relative', 'relative', 
            'relative', 'relative', 'total', 'relative', 'relative', 'total', 'relative', 'total']

    x_data = ['营业总收入', '营业成本', '毛利', '营业税金及附加', '研发费用', '销售费用', 
            '管理费用', '财务费用', '营业利润', '营业外收入', '营业外支出', '利润总额', '所得税费用', '净利润']

    y_data = [
        waterfall_data['营业总收入']/1e8,
        -waterfall_data['营业成本']/1e8,
        waterfall_data['毛利']/1e8,  # 毛利由plotly自动计算
        -waterfall_data['营业税金及附加']/1e8,
        -waterfall_data['研发费用']/1e8,
        -waterfall_data['销售费用']/1e8,
        -waterfall_data['管理费用']/1e8,
        -waterfall_data['财务费用']/1e8,
        waterfall_data['营业利润']/1e8,  # 营业利润由plotly自动计算
        waterfall_data['营业外收入']/1e8,
        -waterfall_data['营业外支出']/1e8,
        waterfall_data['利润总额']/1e8,
        -waterfall_data['所得税费用']/1e8,
        waterfall_data['净利润']/1e8,   # 净利润由plotly自动计算
    ]

    # 创建瀑布图
    fig = go.Figure(go.Waterfall(
        name="利润构成", 
        orientation="v",
        measure=measures,
        x=x_data,
        y=y_data,
        text=[f"{y:.2f}" for y in y_data],  # 添加数据标签
        textposition="outside",              # 标签位置设为外部
    ))

    fig.update_traces(cliponaxis=False)  # 允许文本显示在绘图区域之外

    fig.update_layout(
        title=f"{selected_year}年度利润构成分析",
        height=600,
        showlegend=False,
        xaxis_title="项目",
        yaxis_title="金额（亿元）",
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("营业收入与成本分析")
    
    # 毛利率趋势图
    # 计算毛利率和毛利额
    profit_sheet_10['毛利率'] = (profit_sheet_10['营业总收入'] - profit_sheet_10['营业成本']) / profit_sheet_10['营业总收入'] * 100
    profit_sheet_10['毛利额'] = profit_sheet_10['营业总收入'] - profit_sheet_10['营业成本']

    # 创建双Y轴图表
    fig = go.Figure()

    # 添加毛利额柱状图 (对应左Y轴)
    fig.add_trace(go.Bar(
        x=profit_sheet_10['报告日'],
        y=profit_sheet_10['毛利额']/100000000, # 转换为亿元
        name='毛利额(亿元)',
        yaxis='y',
        text=profit_sheet_10['毛利额']/100000000, # 显示数据标签
        textposition='auto',
        texttemplate='%{text:.2f}'
    ))

    # 添加毛利率折线 (对应右Y轴)
    fig.add_trace(go.Scatter(
        x=profit_sheet_10['报告日'],
        y=profit_sheet_10['毛利率'],
        mode='lines+markers+text',
        name='毛利率(%)',
        marker=dict(size=8, symbol='circle'),
        text=[f'{x:.2f}%' for x in profit_sheet_10['毛利率']],
        textposition='top center',
        yaxis='y2'
    ))

    # 更新布局
    fig.update_layout(
        title='毛利额与毛利率趋势分析',
        xaxis_title='报告期',
        yaxis_title='毛利额(亿元)',
        yaxis2=dict(
            title='毛利率(%)',    # 右侧Y轴标题
            overlaying='y',       # 与左侧Y轴重叠
            side='right'         # 显示在右侧
        ),
        legend=legend
    )

    st.plotly_chart(fig, use_container_width=True) 

    
    # 计算营业收入和营业成本的同比增长率
    profit_sheet_10['营业收入增长率'] = profit_sheet_10['营业收入'].pct_change() * 100
    profit_sheet_10['营业成本增长率'] = profit_sheet_10['营业成本'].pct_change() * 100

    # 创建营业收入与成本增长率对比图
    fig = px.line(profit_sheet_10,
        x='报告日',
        y=['营业收入增长率', '营业成本增长率'],
        title='营业收入与成本增长率对比',
        markers=True
    )

    # 更新布局
    fig.update_layout(
        xaxis_title='报告期',
        yaxis_title='增长率(%)',
        legend=legend
    )

    # 更新文本显示
    for trace in fig.data:
        trace.update(
            mode='lines+markers+text',
            texttemplate='%{y:.1f}%',
            textposition='top center'
        )

    # 添加零增长参考线
    fig.add_hline(y=0, line_dash="dash", line_color="gray")

    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("期间费用分析")
    
    # 计算各项费用率
    profit_sheet_10['销售费用率'] = profit_sheet_10['销售费用'] / profit_sheet_10['营业总收入'] * 100
    profit_sheet_10['管理费用率'] = profit_sheet_10['管理费用'] / profit_sheet_10['营业总收入'] * 100 
    profit_sheet_10['财务费用率'] = profit_sheet_10['财务费用'] / profit_sheet_10['营业总收入'] * 100
    profit_sheet_10['期间费用率'] = profit_sheet_10['销售费用率'] + profit_sheet_10['管理费用率'] + profit_sheet_10['财务费用率']

    # 创建费用率趋势图
    fig = px.line(profit_sheet_10,
        x='报告日',
        y=['期间费用率', '销售费用率', '管理费用率', '财务费用率'],
        title='费用率趋势分析',
        markers=True
    )

    # 更新布局
    fig.update_layout(
        xaxis_title='报告期',
        yaxis_title='费用率(%)',
        legend=legend,
        height=600
    )

    # 更新线条样式
    fig.update_traces(
        mode='lines+markers+text',
        texttemplate='%{y:.2f}%',
        textposition='top center'
    )

    # 设置期间费用率的样式
    fig.data[0].update(
        line=dict(width=4),
        marker=dict(size=10),
        textfont=dict(size=14)
    )

    # 设置其他费用率的样式
    for trace in fig.data[1:]:
        trace.update(
            line=dict(dash='dot'),
        )

    st.plotly_chart(fig, use_container_width=True)

