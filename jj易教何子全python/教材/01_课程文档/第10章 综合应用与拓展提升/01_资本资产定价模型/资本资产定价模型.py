import streamlit as st
import akshare as ak
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import statsmodels.api as sm
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="资本资产定价模型",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 创建Plotly图表的默认配色列表，使用D3调色板
colors = px.colors.qualitative.D3

# 设置图例
legend = dict(
    title=None,
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
)

# 获取沪深300指数和指定股票的日收盘价
@st.cache_data()
def close(code, name, date, date2):
    # 获取沪深300指数的日收盘价
    df_300 = ak.stock_zh_index_daily(symbol="sh000300")
    df_300.date = pd.to_datetime(df_300.date)
    df_300.set_index('date', inplace=True)
    df_300_close = df_300.loc[date:date2, ['close']]
    
    # 获取指定股票的日收盘价
    df_sf = ak.stock_zh_index_daily(symbol=code)
    df_sf.date = pd.to_datetime(df_sf.date)
    df_sf.set_index('date', inplace=True)
    df_sf_close = df_sf.loc[date:date2, ['close']]
    
    # 把df_300_close、df_sf_close进行横向合并
    df_close = pd.concat([df_300_close, df_sf_close], axis=1)
    df_close.columns = ['沪深300指数', name]
    df_close = df_close.pct_change()
    df_close = df_close.dropna()

    return df_close

# 自定义函数 资本资产定价模型
def CAPM(beta, Rm, Rf):
    Rs = Rf + beta * (Rm - Rf)
    return Rs

# 绘制证券市场线
def CAPM_plot(df_close, result):
    # 无风险利率
    LPR = 0.0385
    # 市场收益率
    R_market = 252 * df_close['沪深300指数'].mean()
    # 股权资本成本
    R_stock = CAPM(beta=result.params[1], Rm=R_market, Rf=LPR)
    
    # 创建贝塔值列表
    beta_list = np.linspace(0, 2, 100)
    # 计算贝塔值对应的预期收益率
    R_stock_list = CAPM(beta=beta_list, Rm=R_market, Rf=LPR)
    
    # 绘制证券市场线
    fig3 = go.Figure()
    # 添加轨迹
    fig3.add_trace(go.Scatter(x=beta_list, y=R_stock_list, name='证券市场线', line=dict(color=colors[0], width=2)))
    fig3.add_trace(go.Scatter(x=[result.params[1]], y=[R_stock], name='目标值', marker=dict(color=colors[1], size=10)))
    # 修改布局
    fig3.update_layout(
        title="证券市场线",
        xaxis_title="贝塔值",
        yaxis_title="股票预期收益率",
        legend=legend,
        height=500,
    )
    # 文本注释
    fig3.add_annotation(
        x=result.params[1], 
        y=R_stock,
        text=f"贝塔值等于{round(result.params[1], 4)}对应的收益率",
        arrowhead=1,  # 箭头样式
        arrowwidth=2,  # 箭头宽度
        arrowcolor="#636363",  # 箭头颜色
        ax=30,  # 箭头x轴偏移量
        ay=50,  # 箭头y轴偏移量
        bgcolor="teal",  # 文本框背景颜色
        opacity=0.8,  # 文本框透明度
        font=dict(color="white", size=12, family="Arial"),  # 设置文本字体颜色、大小和字体
    )
    
    return fig3, R_market, result.params[1], R_stock

# 模拟读取股票列表数据
@st.cache_data
def load_stock_list():
    # 读取股票列表
    df = pd.read_excel("01_财务编程开发/03_分析层面/04_财务报表分析/辅助表格 - Tushare/股票列表2.xlsx")
    df[['代码', '市场']] = df['TS代码'].str.split('.', expand=True)
    df['市场代码'] = df['市场'].str.lower() + df['代码'] + '-' + df['股票名称']
    return df['市场代码'].tolist()

# 通用的Markdown文件读取函数
@st.cache_data
def load_markdown_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# 页面标题
st.title("资本资产定价模型")

# 侧边栏 - 基本概念和参数输入
with st.sidebar:
    st.header("参数设置")
    
    # 股票选择
    stock_list = load_stock_list()
    selected_stock = st.selectbox(
        "选择股票",
        options=stock_list,
        index=0
    )
    
    # 日期范围选择
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "开始日期",
            datetime(2018, 1, 1),
            format="YYYY-MM-DD"
        )
    with col2:
        end_date = st.date_input(
            "结束日期",
            datetime(2020, 12, 31),
            format="YYYY-MM-DD"
        )
    
    # 显示基础参数
    st.markdown("### 模型参数")
    st.markdown("**无风险收益率:** 3.85%")
    
    # 分割线
    st.markdown("---")
    
    # 计算结果会在这里显示（占位）
    st.markdown("### 计算结果")
    calc_result_container = st.container()
    
    # 分割线
    st.markdown("---")
    
    # 基本概念卡片
    st.markdown("### 基本概念")
    st.markdown("""
    资本资产定价模型（CAPM）是金融学中的重要模型，描述股票预期收益与系统性风险的关系。
    
    CAPM 公式：
    
    $E(R_i) = R_f + \\beta_i (E(R_m) - R_f)$
    
    其中：
    - $E(R_i)$ 是资产 i 的预期收益率
    - $R_f$ 是无风险收益率
    - $\\beta_i$ 是资产 i 的贝塔系数
    - $E(R_m)$ 是市场预期收益率
    """)
    
    # 提示信息
    st.warning("""
    **注意：** CAPM 中的 β 值衡量个股相对于市场的波动性，但通常基于历史数据计算，
    在未来时间内不一定保持稳定。尤其在市场剧烈波动或公司结构、业务发生变化时，
    β 可能失去代表性。
    """)

# 主要内容区
# 显示加载状态
with st.spinner("正在加载数据和计算模型..."):
    # 解析股票代码和名称
    code, name = selected_stock.split('-')
    
    # 获取数据
    df_close = close(code, name, start_date, end_date)
    df_close_display = df_close.reset_index()
    df_close_display['date'] = df_close_display['date'].dt.strftime('%Y-%m-%d')
    
    # 计算回归分析
    fig2 = px.scatter(
        df_close,
        x='沪深300指数',
        y=name,
        trendline="ols",
        title='基于回归直线法的贝塔值',
        color_discrete_sequence=colors
    ).update_layout(
        legend=legend,
        height=500,
    )
    
    # 获取回归结果
    results = px.get_trendline_results(fig2)
    result = results.px_fit_results.iloc[0]
    
    # 计算证券市场线
    fig3, R_market, beta, R_stock = CAPM_plot(df_close, result)
    
    # 创建股票日收益率图表
    fig1 = px.line(
        df_close,
        title='股票日收益率',
        color_discrete_sequence=colors
    ).update_layout(
        legend=legend,
        height=500,
    )
    fig1.update_xaxes(tickformat="%Y-%m")
    
    # 在侧边栏显示计算结果
    with calc_result_container:
        st.markdown(f"""
        | 参数 | 数值 |
        | --- | --- |
        | 市场的预期收益率 | {R_market:.2%} |
        | 资产的Beta系数 | {beta:.4f} |
        | 资产的预期收益率 | {R_stock:.2%} |
        """)
    
    # 创建主内容区
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["股票日收益率", "回归分析", "证券市场线"])
    
    with tab1:
        # 在股票日收益率选项卡中显示图表和数据表格
        st.markdown("### 股票日收益率")
        st.plotly_chart(fig1, use_container_width=True)
        
        # 使用折叠组件显示收益率数据
        with st.expander("详细数据", expanded=False):
            st.markdown("### 收益率数据")
            st.dataframe(
                df_close_display,
                use_container_width=True,
                hide_index=True
            )
            
            # 添加统计性描述表格
            st.markdown("### 统计性描述")
            # 计算统计量
            stats_df = df_close[[name, '沪深300指数']].describe().T
            
            # 设置样式函数 - 根据数据大小显示不同背景色
            def style_dataframe(df):
                # 保留原始数据格式化
                df_styled = df.style.format({
                    'mean': '{:.4%}',
                    'std': '{:.4%}',
                    'min': '{:.4%}',
                    '25%': '{:.4%}',
                    '50%': '{:.4%}',
                    '75%': '{:.4%}',
                    'max': '{:.4%}',
                })
                
                # 添加背景色 - 对每一列应用渐变色：红色渐变
                df_styled = df_styled.background_gradient(cmap='Reds')
                
                return df_styled
            
            # 应用样式
            formatted_stats = style_dataframe(stats_df)
            st.dataframe(formatted_stats, use_container_width=True)
            
            # 添加相关性热图
            st.markdown("### 相关性分析")
            corr = df_close[[name, '沪深300指数']].corr()
            # 设置相关系数矩阵的样式:
            # - 保留4位小数
            # - 使用coolwarm配色方案设置背景色渐变,正相关为红色,负相关为蓝色
            # 相关系数(ρ)：仅衡量两个变量变动方向的一致性，范围在[-1,1]之间
            # 贝塔系数(β)：衡量股票相对于市场的波动幅度，理论上可以是任何实数
            corr_styled = corr.style.format('{:.4f}').background_gradient(cmap='coolwarm')
            st.dataframe(corr_styled, use_container_width=True)
                            
    with tab2:
        # 在回归分析选项卡中先显示图表
        st.markdown("### 基于回归直线法的贝塔值")
        st.plotly_chart(fig2, use_container_width=True)
        
        # 在图形下方显示按钮和弹出内容
        col_buttons = st.columns(3)
        
        # OLS回归结果弹出框
        with col_buttons[0]:
            with st.popover("查看OLS回归详细结果", use_container_width=True):
                # 使用st.code()替代st.text()，确保显示对齐
                st.code(str(result.summary()), language="text")
                
                # 添加一个美化版本的关键结果摘要
                st.markdown("#### 关键结果摘要")
                key_results = pd.DataFrame({
                    "参数": ["Beta", "常数项"],
                    "值": [
                        f"{result.params[1]:.4f}",
                        f"{result.params[0]:.4f}"
                    ]
                })
                st.dataframe(key_results, use_container_width=True, hide_index=True)
        
        # 回归参数说明弹出框
        with col_buttons[1]:
            with st.popover("回归参数说明", use_container_width=True):
                参数说明 = load_markdown_file("06_课程/03_资本资产定价模型/参数说明.md")
                st.markdown(参数说明)
        
        # 帮助说明弹出框
        with col_buttons[2]:
            with st.popover("贝塔值计算帮助", use_container_width=True):
                计算帮助 = load_markdown_file("06_课程/03_资本资产定价模型/计算帮助.md")
                st.markdown(计算帮助)
        
    with tab3:
        # 证券市场线图表
        st.markdown("### 证券市场线")
        st.plotly_chart(fig3, use_container_width=True)