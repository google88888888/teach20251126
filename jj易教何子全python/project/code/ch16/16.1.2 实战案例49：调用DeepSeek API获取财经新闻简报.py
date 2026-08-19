import re
import os
from pathlib import Path
from openai import OpenAI
from typing import Optional


def save_markdown_content(content: str, filename: str = "output.md") -> Optional[str]:
    """
    将内容保存为 Markdown 文件，自动处理已存在的文件名冲突

    :param content: 要保存的 Markdown 内容
    :param filename: 目标文件名（默认 output.md）
    :return: 成功返回保存路径，失败返回 None
    """
    try:
        # 处理文件已存在的情况，避免覆盖
        output_path = Path(filename)
        if output_path.exists():
            base_name = output_path.stem  # 获取文件名（不包括扩展名）
            suffix = output_path.suffix   # 获取文件扩展名
            counter = 1
            while output_path.exists():
                output_path = Path(f"{base_name}_{counter}{suffix}")  # 生成新的文件名
                counter += 1

        # 确保目标目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 将内容写入 Markdown 文件
        with output_path.open("w", encoding="utf-8") as f:
            f.write(content)

        return str(output_path)

    except Exception as e:
        print(f"文件保存失败: {str(e)}")
        return None


def fetch_and_save_news(
        output_file: str = "news_report.md",
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com"
) -> bool:
    """
    通过 DeepSeek API 获取财经新闻摘要，并保存为 Markdown 文件

    :param output_file: 输出文件名
    :param api_key: DeepSeek API 密钥（若未提供，则尝试从环境变量读取）
    :param base_url: API 基础 URL
    :return: 是否成功执行
    """
    try:
        # 获取 API 密钥（如果未提供，则从环境变量 DEEPSEEK_API_KEY 获取）
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("API 密钥未提供，且环境变量中未找到 DEEPSEEK_API_KEY")

        # 初始化 OpenAI（DeepSeek API）客户端
        client = OpenAI(api_key=api_key, base_url=base_url)

        # 发送 API 请求，获取财经新闻摘要
        response = client.chat.completions.create(
            model="deepseek-chat",  # 选择 DeepSeek 的聊天模型
            messages=[
                {"role": "system", "content": "你是一个专业的财经分析师"},  # 设定 AI 角色
                {"role": "user",
                 "content": "请通过联网搜索最新财经新闻，生成包含时间、来源和关键数据的简报，返回 Markdown 格式代码。"},
            ],
            stream=False  # 不使用流式响应，直接返回完整结果
        )

        # 提取 API 返回的文本内容
        response_content = response.choices[0].message.content
        print("API 返回内容：", response_content)

        # 使用正则表达式匹配 Markdown 代码块
        markdown_blocks = re.findall(
            r"```markdown\s*(.*?)\s*```",  # 匹配以 ```markdown 开头的代码块
            response_content,
            flags=re.DOTALL | re.IGNORECASE
        )

        if not markdown_blocks:
            print("响应中未找到有效的 Markdown 代码块")
            return False

        # 合并多个 Markdown 代码块（如果有）
        combined_content = "\n\n---\n\n".join(
            [block.strip() for block in markdown_blocks]
        )

        # 将 Markdown 内容保存到文件
        saved_path = save_markdown_content(combined_content, output_file)
        if saved_path:
            print(f"成功保存报告至：{saved_path}")
            return True
        return False

    except Exception as e:
        print(f"操作失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 运行示例，建议 API 密钥通过环境变量传递，而非直接硬编码
    result = fetch_and_save_news(
        output_file="daily_finance_report.md",
        api_key="<DeepSeek API Key>"  # 出于安全考虑，建议改为环境变量
    )
    print("执行结果:", "成功" if result else "失败")
