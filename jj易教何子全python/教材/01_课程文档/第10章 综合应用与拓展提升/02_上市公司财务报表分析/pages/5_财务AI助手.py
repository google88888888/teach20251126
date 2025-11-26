import streamlit as st
from http import HTTPStatus
from dashscope import Generation

# 设置页面标题
st.set_page_config(
    page_title="财务AI助手",
    page_icon="🤖",
    layout="wide"
)

# 设置页面标题
st.title("AI 助手")

# 检查是否已选择股票
if not st.session_state.get("selected_stock"):
    st.info("请在首页选择要分析的股票")
else:
    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": f"你是一个专业的财务分析师，你可以帮助用户进行财务分析，回答用户的问题，并提供相关的建议和信息。\n当前选择的上市公司是：{st.session_state.selected_stock}"},
            {"role": "assistant", "content": "你好，请问有什么我可以帮你的吗？😊"}
        ]

    # 获取AI回复函数
    def get_ai_response(placeholder):
        try:
            responses = Generation.call(
                api_key='',
                model="qwen-plus",
                messages=st.session_state.messages,
                result_format='message',
                stream=True,
                enable_search=True,
                top_p=0.8
            )
            
            for response in responses:
                if response.status_code == HTTPStatus.OK:
                    full_response = response.output.choices[0]['message']['content']
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            return full_response
        except Exception as e:
            error_msg = f"发生错误: {str(e)}"
            placeholder.error(error_msg)
            return error_msg

    # 显示聊天历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 聊天输入
    if prompt := st.chat_input("请输入您的问题..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response = get_ai_response(response_placeholder)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

    # 清除聊天历史的按钮
    if st.button("清除聊天历史"):
        st.session_state.messages = [
            {"role": "system", "content": f"你是一个专业的财务分析师，你可以帮助用户进行财务分析，回答用户的问题，并提供相关的建议和信息。\n当前选择的上市公司是：{st.session_state.selected_stock}"},
            {"role": "assistant", "content": "你好，请问有什么我可以帮你的吗？😊"}
        ]
        st.rerun()