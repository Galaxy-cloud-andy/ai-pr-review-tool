import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件里隐藏的密码
load_dotenv()

def get_pr_diff(pr_url: str):
    # 转换 API 链接
    api_url = (
        pr_url.strip()
        .replace("https://github.com/", "https://api.github.com/repos/", 1)
        .replace("/pull/", "/pulls/", 1)
    )

    # 组装请求头，安全读取 Token
    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "User-Agent": "ai-pr-review-tool",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }

    # 发送请求
    try:
        resp = requests.get(api_url, headers=headers, timeout=30)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    # 返回结果
    if resp.status_code == 200:
        return resp.text

    print(f"Request failed: {resp.status_code} {resp.reason}")
    return None


def analyze_code_diff(diff_text: str) -> str:
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.deepseek.com",
    )
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个资深的代码审查专家。请用中文对下面这段 Git Diff 代码变更进行 Review，"
                        "指出代码的优点，并提出潜在的问题或修改建议，保持专业且简明扼要。"
                    ),
                },
                {"role": "user", "content": diff_text},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI review failed: {e}")
        return ""


# 测试运行
diff_text = get_pr_diff("https://github.com/Galaxy-cloud-andy/ai-pr-review-tool/pull/1")
if diff_text:
    review_result = analyze_code_diff(diff_text)
    print(review_result)