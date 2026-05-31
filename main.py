import os
import sys
import requests
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件里隐藏的密码
load_dotenv()

def test_func():
    a = 1
    b = 2
    c = a/0
    return c
def get_pr_diff(repo: str, pr_number: str):
    api_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "User-Agent": "ai-pr-review-tool",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    }

    try:
        resp = requests.get(api_url, headers=headers, timeout=30)
    except requests.RequestException as e:
        print(f"获取 Diff 失败: {e}")
        return None

    if resp.status_code == 200:
        return resp.text

    print(f"获取 Diff 失败: {resp.status_code} {resp.reason}")
    return None


def post_comment_to_pr(repo: str, pr_number: str, comment: str):
    api_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ai-pr-review-tool",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    }

    payload = {"body": comment}

    try:
        resp = requests.post(api_url, headers=headers, json=payload, timeout=30)
    except requests.RequestException as e:
        print(f"发送评论失败: {e}")
        return False

    if resp.status_code in (200, 201):
        return True

    print(f"发送评论失败: {resp.status_code} {resp.reason} {resp.text}")
    return False


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
                        "你是一个资深的大厂代码审查专家。请仔细阅读以下 Git Diff 代码变更，并使用精美的 Markdown 格式输出结构化的中文 Review 报告。\n\n"
                        "请严格按以下模板输出：\n"
                        "### 🌟 变更总结\n"
                        "- 简要概括此次代码变动的核心目的。\n\n"
                        "### 🐛 风险与漏洞 (若无请写“未发现显著风险”)\n"
                        "- 指出可能存在的逻辑漏洞、异常处理缺失或性能隐患。\n\n"
                        "### 💡 优化建议与代码重构\n"
                        "- 提供具体的代码改进建议，并使用 Markdown 代码块提供重构后的最佳实践代码。\n"
                    ),
                },
                {"role": "user", "content": diff_text},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI review failed: {e}")
        return ""


print("开始读取 GitHub Actions 环境变量...")
repo = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

if not repo or not pr_number:
    print("缺少必要环境变量 GITHUB_REPOSITORY 或 PR_NUMBER，程序退出。")
    sys.exit(1)

print("开始获取 Diff...")
diff_text = get_pr_diff(repo, pr_number)
if not diff_text:
    print("未获取到 Diff，程序退出。")
    sys.exit(1)

max_diff_length = 20000
if len(diff_text) > max_diff_length:
    print(f"Diff 过长，已截断到 {max_diff_length} 字符以防超载。")
    diff_text = diff_text[:max_diff_length]


print("Diff 获取完成，开始 AI 分析...")
review_result = analyze_code_diff(diff_text)
if not review_result:
    print("AI 分析失败，程序退出。")
    sys.exit(1)

final_comment = (
    f"{review_result}\n\n"
    f"---\n"
    f"> 🤖 *Powered by [DeepSeek] & GitHub Actions | 全自动代码审查助手*"
)

print("AI 分析完成，正在发送评论...")
if post_comment_to_pr(repo, pr_number, final_comment):
    print("评论发送成功。")
else:
    print("评论发送失败。")
    sys.exit(1)
