import os
import sys
import requests
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件里隐藏的密码
load_dotenv()


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

print("AI 分析完成，正在发送评论...")
if post_comment_to_pr(repo, pr_number, review_result):
    print("评论发送成功。")
else:
    print("评论发送失败。")
    sys.exit(1)
