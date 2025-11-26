import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import akshare as ak

# 设置页面配置
st.set_page_config(
    page_title="财务报表分析仪表板",
    page_icon="📊",
    layout="wide",
)

# 初始化 session state
# 检查session state中是否已存在selected_stock变量
# 如果不存在，则初始化为None，表示用户尚未选择股票
if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = None

# 读取股票列表
@st.cache_data
def load_stock_list():
    stock_codes = pd.read_excel(r'dashboard\streamlit\我的案例\财务报表分析仪表板2\stock_codes.xlsx')
    stock_codes['code'] = stock_codes['code'].astype(str).str.zfill(6)  # 用0填充到6位
    stock_codes['display'] = stock_codes['code'] + ' - ' + stock_codes['name']
    return stock_codes

# 加载数据
@st.cache_data
def load_data(stock_code):
    # 在线获取财务报表数据
    balance_sheet_df = ak.stock_financial_report_sina(stock=stock_code, symbol="资产负债表")
    profit_sheet_df = ak.stock_financial_report_sina(stock=stock_code, symbol="利润表")
    cash_flow_df = ak.stock_financial_report_sina(stock=stock_code, symbol="现金流量表")
    financial_indicators_df = ak.stock_financial_analysis_indicator(symbol=stock_code)
    
    # 数据预处理
    for df in [balance_sheet_df, profit_sheet_df, cash_flow_df]:
        df['报告日'] = df['报告日'].astype(str)
    
    # 财务指标数据预处理
    financial_indicators_df['日期'] = financial_indicators_df['日期'].astype(str)
        
    return balance_sheet_df, profit_sheet_df, cash_flow_df, financial_indicators_df

# 侧边栏
with st.sidebar:
    
    # 加载股票列表
    stock_list = load_stock_list()
    
    # 选择股票
    st.header("🔍 选择股票")
    # 创建一个下拉选择框让用户选择股票
    # options参数提供所有可选的股票列表
    # index参数设置默认选中项：如果session state中没有选中的股票则为None，否则查找当前选中股票的索引
    # placeholder参数设置未选择时的提示文本
    # key参数为此组件指定唯一标识符
    selected_stock = st.selectbox(
        "请选择要分析的股票:",
        options=stock_list['display'].tolist(),
        index=None if st.session_state.selected_stock is None 
              else stock_list['display'].tolist().index(st.session_state.selected_stock),
        placeholder="搜索或选择股票...",
        key="stock_selector"
    )
    
    # 更新 session state
    # 如果用户选择了股票，则更新session state中的选中股票
    if selected_stock is not None:
        st.session_state.selected_stock = selected_stock
        
    # 如果session state中有选中的股票，则显示成功消息
    if st.session_state.selected_stock:
        st.success(f"当前选中: {st.session_state.selected_stock}")

# 加载数据到session state
if st.session_state.selected_stock:
    # 从选中的股票字符串中提取股票代码
    stock_code = st.session_state.selected_stock.split(' - ')[0]

    # 调用load_data函数获取四种财务报表数据
    balance_sheet_df, profit_sheet_df, cash_flow_df, financial_indicators_df = load_data(stock_code)
    # 将获取的数据存储到session state中，以便在应用的不同部分使用
    st.session_state['balance_sheet_df'] = balance_sheet_df  # 资产负债表
    st.session_state['profit_sheet_df'] = profit_sheet_df    # 利润表
    st.session_state['cash_flow_df'] = cash_flow_df          # 现金流量表
    st.session_state['financial_indicators_df'] = financial_indicators_df  # 财务指标

    # 从session state获取数据
    balance_sheet_df = st.session_state.balance_sheet_df
    profit_sheet_df = st.session_state.profit_sheet_df
    cash_flow_df = st.session_state.cash_flow_df
    financial_indicators_df = st.session_state.financial_indicators_df

    # 主页内容
    st.title("欢迎使用财务报表分析仪表板 🎯")
    st.markdown("---")

    # 显示当前选择的公司
    st.markdown(f"### 关键指标")

    # 获取2023年和2022年数据
    latest_bs_data = balance_sheet_df[
        balance_sheet_df['报告日'].str.endswith('1231')
    ].iloc[0]

    prev_bs_data = balance_sheet_df[
        balance_sheet_df['报告日'].str.endswith('1231')
    ].iloc[1]

    latest_pl_data = profit_sheet_df[
        profit_sheet_df['报告日'].str.endswith('1231')
    ].iloc[0]

    prev_pl_data = profit_sheet_df[
        profit_sheet_df['报告日'].str.endswith('1231')
    ].iloc[1]

    # 计算同比变化率
    def calc_yoy(current, previous):
        return (current - previous) / abs(previous) * 100

    # 计算同比变化率并格式化显示
    def format_delta(current, previous):
        yoy = calc_yoy(current, previous)
        return f"{yoy:.1f}%"

    # 创建指标容器
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="资产合计（亿元）",
            value=f"{latest_bs_data['资产总计']/100000000:.2f}",
            delta=format_delta(latest_bs_data['资产总计'], prev_bs_data['资产总计']),
            delta_color="normal"
        )

    with col2:
        st.metric(
            label="负债合计（亿元）",
            value=f"{latest_bs_data['负债合计']/100000000:.2f}",
            delta=format_delta(latest_bs_data['负债合计'], prev_bs_data['负债合计']),
            delta_color="normal"
        )

    with col3:
        st.metric(
            label="所有者权益合计（亿元）",
            value=f"{latest_bs_data['所有者权益(或股东权益)合计']/100000000:.2f}",
            delta=format_delta(latest_bs_data['所有者权益(或股东权益)合计'], prev_bs_data['所有者权益(或股东权益)合计']),
            delta_color="normal"
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric(
            label="营业收入（亿元）",
            value=f"{latest_pl_data['营业总收入']/100000000:.2f}",
            delta=format_delta(latest_pl_data['营业总收入'], prev_pl_data['营业总收入']),
            delta_color="normal"
        )

    with col5:
        delta = calc_yoy(latest_pl_data['营业成本'], prev_pl_data['营业成本'])
        st.metric(
            label="营业成本（亿元）",
            value=f"{latest_pl_data['营业成本']/100000000:.2f}",
            delta=f"{delta:.1f}%",
            delta_color="normal"
        )

    with col6:
        st.metric(
            label="净利润（亿元）",
            value=f"{latest_pl_data['净利润']/100000000:.2f}",
            delta=format_delta(latest_pl_data['净利润'], prev_pl_data['净利润']),
            delta_color="normal"
        )

    def stream_analysis(latest_bs_data, prev_bs_data, latest_pl_data, prev_pl_data):
        # 计算同比变化
        asset_yoy = calc_yoy(latest_bs_data['资产总计'], prev_bs_data['资产总计'])
        liability_yoy = calc_yoy(latest_bs_data['负债合计'], prev_bs_data['负债合计'])
        equity_yoy = calc_yoy(latest_bs_data['所有者权益(或股东权益)合计'], prev_bs_data['所有者权益(或股东权益)合计'])
        revenue_yoy = calc_yoy(latest_pl_data['营业总收入'], prev_pl_data['营业总收入'])
        cost_yoy = calc_yoy(latest_pl_data['营业成本'], prev_pl_data['营业成本'])
        profit_yoy = calc_yoy(latest_pl_data['净利润'], prev_pl_data['净利润'])
        
        # 生成分析文本
        analysis_text = [
            "根据最新财务数据分析，公司整体经营情况如下：\n\n",
            "1. 资产状况：\n",
            f"   公司总资产为{latest_bs_data['资产总计']/100000000:.2f}亿元，较上年同期{('增长' if asset_yoy > 0 else '下降')}{abs(asset_yoy):.1f}%。\n",
            f"   负债总额为{latest_bs_data['负债合计']/100000000:.2f}亿元，同比{('增长' if liability_yoy > 0 else '下降')}{abs(liability_yoy):.1f}%。\n",
            f"   所有者权益达到{latest_bs_data['所有者权益(或股东权益)合计']/100000000:.2f}亿元，同比{('增长' if equity_yoy > 0 else '下降')}{abs(equity_yoy):.1f}%。\n\n",
            "2. 经营成果：\n",
            f"   公司实现营业收入{latest_pl_data['营业总收入']/100000000:.2f}亿元，同比{('增长' if revenue_yoy > 0 else '下降')}{abs(revenue_yoy):.1f}%。\n",
            f"   营业成本为{latest_pl_data['营业成本']/100000000:.2f}亿元，同比{('增长' if cost_yoy > 0 else '下降')}{abs(cost_yoy):.1f}%。\n",
            f"   最终实现净利润{latest_pl_data['净利润']/100000000:.2f}亿元，同比{('增长' if profit_yoy > 0 else '下降')}{abs(profit_yoy):.1f}%。\n\n",
            "3. 财务分析：\n"
        ]
        
        # 添加财务分析结论
        if revenue_yoy > 0 and profit_yoy > 0:
            analysis_text.append("   公司收入和利润均实现正增长，经营状况良好。")
        elif revenue_yoy > 0 and profit_yoy < 0:
            analysis_text.append("   虽然收入有所增长，但利润下滑，需关注成本控制情况。")
        elif revenue_yoy < 0 and profit_yoy > 0:
            analysis_text.append("   虽然收入有所下滑，但通过成本控制实现了利润增长。")
        else:
            analysis_text.append("   收入和利润均出现下滑，经营压力较大。")
        
        if cost_yoy > revenue_yoy:
            analysis_text.append("\n   成本增速快于收入增速，需警惕成本控制问题。")
        else:
            analysis_text.append("\n   成本增速低于收入增速，运营效率有所提升。")
        
        # 逐字输出
        for sentence in analysis_text:
            for word in sentence:
                yield word
                time.sleep(0.02)

    # 添加分析文本
    st.markdown("### 财务分析")

    # 使用st.write_stream流式输出分析结果
    st.write_stream(stream_analysis(latest_bs_data, prev_bs_data, latest_pl_data, prev_pl_data))

else:
    st.info("请在左侧选择一个股票开始分析")
