# multi-ai-skills

[![tests](https://github.com/xuyewild/multi-ai-skills/actions/workflows/tests.yml/badge.svg)](https://github.com/xuyewild/multi-ai-skills/actions/workflows/tests.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[English](README.md) | 中文

让多个 AI（Claude、Codex、ChatGPT、子 agent）一起做长项目时不乱、不白花钱的两个 skill。来自半年 AI 漫剧生产实战：一个导演，加上几个 AI，几十集、每天几十次付费视频生成、每天换好几个对话。

| skill | 解决什么 |
|---|---|
| [multi-ai-handoff](skills/zh/multi-ai-handoff/SKILL.md) | 谁执行、谁检查、谁拍板；按文件交接；交接前独立复核；按难度选模型；付费生成先记账再点 |
| [project-memory](skills/zh/project-memory/SKILL.md) | 项目文件夹就是记忆；人的纠正按类写回；规则台账只记人定过的；新对话按文件判断接到哪一步 |

两个 skill 可以单独用，一起用效果最好。每个都有中文版 `skills/zh/` 和英文版 `skills/en/`，内容一致，各自完整可装。

## 适合谁

- 用 AI 做视频、图像、长文档、多轮代码，项目要做很多天、跨很多对话
- 同时用两个以上 AI，或者用子 agent 分工
- 有付费生成，返工很贵

单次问答用不上。

## 核心几句

- **AI 之间只认文件，不认对话。** 进度 = 文件夹里有什么。
- **每次交接都有独立的人检查。** 作者不给自己下“通过”。复核记录带文件哈希，文件一改自动失效。
- **花钱和拍板只归人。** 付费动作先预留、只点一次、再结算；点了不确定就先对账，不重按。
- **按难度选档。** `S = 2N + 2K + A + F − 2E`，高档模型只用在设计上。
- **只记人定过的规则，原话原样抄。** AI 的推测不写成规则。

## 30 秒例子

付费动作账本：上一次点了但状态不明，就不让再点：

```console
$ S=skills/zh/multi-ai-handoff/scripts/ledger.py
$ python3 $S demo.json init --unit credits --limit 500
ok
$ python3 $S demo.json reserve --id shot1-a1 --item shot1 --cost 120
ok
$ python3 $S demo.json unknown --id shot1-a1      # 点了，不确定平台收没收到
ok
$ python3 $S demo.json reserve --id shot1-a2 --item shot1 --cost 120 --kind retry
REFUSED shot1 has an attempt in state `unknown`; reconcile with the platform first
```

## 安装

**Claude Code**：把要用的 skill 文件夹复制到 `~/.claude/skills/`（全局）或项目里的 `.claude/skills/`。

```bash
git clone https://github.com/xuyewild/multi-ai-skills
cp -r multi-ai-skills/skills/zh/multi-ai-handoff ~/.claude/skills/
cp -r multi-ai-skills/skills/zh/project-memory ~/.claude/skills/
```

想用分档子 agent，把 `skills/zh/multi-ai-handoff/templates/tier-agents/` 和 `templates/independent-reviewer.md` 复制到项目的 `.claude/agents/`。

**Claude 网页版或桌面版**：把 skill 文件夹打成 zip，在设置里上传为自定义 skill。

**其他 AI**：skill 就是 Markdown 加 Python 脚本，把 `SKILL.md` 和用到的参考文件交给它读即可。

## 脚本

只用 Python 标准库，3.9 以上。

| 脚本 | 做什么 |
|---|---|
| `multi-ai-handoff/scripts/review_gate.py` | 记录复核结论和文件哈希，交接前检查放不放行 |
| `multi-ai-handoff/scripts/ledger.py` | 付费动作账本：预算、重试上限、状态不明不重按 |
| `project-memory/scripts/check_project.py` | 巡检规则台账格式和项目关键文件 |

```bash
python -m unittest discover -s tests -v
```

## 贡献

欢迎 issue 和 PR，尤其是你在自己项目里用过之后遇到的问题。改规则请说明在什么场景出过什么问题。

## 许可证

[MIT](LICENSE)
