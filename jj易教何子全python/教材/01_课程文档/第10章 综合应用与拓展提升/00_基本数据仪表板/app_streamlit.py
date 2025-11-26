import streamlit as st
import plotly.express as px
import pandas as pd

# 设置页面配置
st.set_page_config(layout="wide")

# 获取数据
df = px.data.gapminder()
# 将列标题翻译为中文
df.columns = ['国家', '大洲', '年份', '预期寿命', '人口', '人均GDP', 'ISO代码', 'ISO编号']

# 创建左右两栏布局
left_col, right_col = st.columns([4, 6])

# 设置图表高度 (考虑标题和间距后，左侧每个图表约350px)
CHART_HEIGHT = 350

# 左侧栏 - 条形图和旭日图
with left_col:
    # 条形图部分
    st.header("各国平均人均GDP前20名")
    # 按国家汇总GDP并降序排序取前20名
    df_sorted = df.groupby('国家')['人均GDP'].mean().sort_values(ascending=False).head(20).iloc[::-1]
    
    # 绘制横向条形图
    fig_bar = px.bar(df_sorted,
                     x=df_sorted.values,  # x轴数据(人均GDP)
                     y=df_sorted.index,   # y轴数据(国家)
                     orientation='h',      # 设置为横向
                     height=CHART_HEIGHT,
                     labels={'x': '平均人均GDP (美元)', 'y': '国家'})
    
    # 翻转图表使x轴在上方并调整边距
    fig_bar.update_layout(
        autosize=True,
        xaxis={'side': 'top'},
        margin=dict(t=30, l=25, r=25, b=25),  # 减小上边距
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.header("各大洲平均预期寿命")
    # 按大洲计算平均预期寿命
    df_life = df.groupby(['大洲'])['预期寿命'].mean().reset_index()
    
    # 绘制树状图
    fig_tree = px.treemap(df_life,
                         path=['大洲'],  # 定义层级路径
                         values='预期寿命',      # 数值大小决定矩形面积
                         height=CHART_HEIGHT)  # 高度设为左侧两个图表的总高度加上header间距
    
    # 更新布局
    fig_tree.update_layout(
        margin=dict(t=30, l=25, r=25, b=25),  # 减小上边距
    )
    
    st.plotly_chart(fig_tree, use_container_width=True)


# 右侧栏 - 树状图
with right_col:

    # 旭日图部分
    st.header("各大洲不同国家的平均预期寿命")
    # 按年份和大洲计算平均预期寿命
    df_life_by_year = df.groupby(['国家', '大洲'])['预期寿命'].mean().reset_index()
    
    # 绘制旭日图
    fig_sun = px.sunburst(df_life_by_year,
                         path=['大洲', '国家'],  # 定义层级路径
                         values='预期寿命',      # 数值大小决定扇形面积
                         height=CHART_HEIGHT * 2 + 100)
    
    # 更新布局
    fig_sun.update_layout(
        margin=dict(t=30, l=25, r=25, b=25),  # 减小上边距
    )
    
    st.plotly_chart(fig_sun, use_container_width=True)