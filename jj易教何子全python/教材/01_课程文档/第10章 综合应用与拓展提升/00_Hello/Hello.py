import streamlit as st

st.set_page_config(
    page_title="你好",
    page_icon="👋",
)

st.write("# 欢迎使用 Streamlit! 👋")

st.sidebar.success("请在上方选择一个演示。")

st.markdown(
    """
    Streamlit 是一个专门为机器学习和数据科学项目构建的开源应用框架。
    **👈 从侧边栏选择一个演示** 来查看 Streamlit 能做什么!
    ### 想了解更多?
    - 访问 [streamlit.io](https://streamlit.io)
    - 查看我们的[文档](https://docs.streamlit.io)
    - 在我们的[社区论坛](https://discuss.streamlit.io)提问
    ### 查看更多复杂的演示
    - 使用神经网络[分析 Udacity 自动驾驶汽车图像数据集](https://github.com/streamlit/demo-self-driving)
    - 探索[纽约市共享乘车数据集](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)