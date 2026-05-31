🤖 AI PR Review 助手

> 体验方式一（最快）： 请直接点击仓库上方的 `Pull requests` 标签，查看名为 **`[Demo] 体验与效果展示专用 PR`** 的记录，即可直接观看机器人自动生成的 Review 报告。
> 体验方式二： 可以直接 Fork 本仓库并提交一个 PR，机器人将在 1 分钟内自动在评论区回复审查结果。

**[👉 🎥 点击此处观看项目完整 Demo 演示视频 (B站) 👈](https://www.bilibili.com/video/BV1j6VS6KEMN/?spm_id_from=333.1387.homepage.video_card.click&vd_source=41173aea8e2c13afb4e5e861b43e8dee)**


## 📖 项目简介
本项目是一个基于 Python、GitHub Actions 和 DeepSeek 大模型构建的**全自动代码审查（Code Review）工具**。
当开发者提交 Pull Request 时，云端机器人会自动抓取代码变更，进行深度的静态分析，并在评论区输出结构化的评审意见，帮助团队提升代码质量与合并效率。

## 🧠 核心设计思路

### 1. 架构图与工作流
本项目采用轻量级的无服务器架构（Serverless），完全依赖 GitHub Actions 驱动：
`开发者提交 PR` ➡️ `触发 GitHub Actions` ➡️ `Python 脚本提取 PR Diff` ➡️ `调用大模型 API 分析` ➡️ `GitHub API 回写评论`

### 2. 模型选择及原因
本项目选择 DeepSeek作为核心 AI 引擎。
 **推理能力极强**：在代码逻辑理解和 Bug 发现方面，DeepSeek 稳居国内大模型第一梯队。
 **极高的性价比**：API 价格极其亲民，适合高频次的 CI/CD 自动化调用。
 **生态兼容性好**：底层 API 完美兼容 OpenAI 标准，降低了接入和后期迁移的开发成本。

### 3. 上下文获取方式
单纯的代码 Diff 往往缺乏完整的上下文逻辑。本项目的上下文获取策略为：
 **基础获取**：利用 GitHub REST API 抓取特定 PR 的完整 Diff 文本。
 **上下文补全**：解析 Diff 信息，针对修改的关键文件，提取上下文背景，合并后一并构建至 Prompt 中发送给 AI，从而极大降低了 AI 的“幻觉”率。

## 🛠️ 如何快速复刻？ (Quick Start)
如果你想在自己的 GitHub 仓库中使用本工具，仅需 2 步，**无需在本地运行任何代码**：

1. **复制核心文件**：将本仓库的 `main.py`、`requirements.txt` 以及 `.github/workflows/review.yml` 直接拷贝到您的项目中。
2. **配置环境变量**：在您仓库的 `Settings` -> `Secrets and variables` -> `Actions` 中，新建一个名为 `OPENAI_API_KEY` 的 Secret，填入您申请的 DeepSeek API Key 即可。
*(注：GitHub Token 会在运行期自动生成，无需手动配置。)*

## 🚀 未来扩展方向
虽然目前已经跑通了，但未来本项目有以下扩展规划：
1. **多语言专属规则检测**：针对 Python、Java、C++ 等不同语言，在 Prompt 中注入不同的静态检查规范（如 PEP8 规范检查）。
2. **长文本超载处理**：当 PR 变更极大的时候，引入 Token 截断机制或文件分块（Chunking）审查，避免超出大模型的上下文窗口。
3. **自定义 Prompt 模板**：允许用户在项目根目录放置 `.pr_review_config.yaml` 文件，自定义他们希望 AI 关注的审查重点（比如偏向安全性检查，还是偏向性能优化）。
