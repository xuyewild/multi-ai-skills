# multi-ai-skills

[![tests](https://github.com/xuyewild/multi-ai-skills/actions/workflows/tests.yml/badge.svg)](https://github.com/xuyewild/multi-ai-skills/actions/workflows/tests.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[English](README.md) | 中文

我用 Claude 和 Codex 做了半年 AI 漫剧，到现在几千条片子，一天要开好几个新对话。

做久了发现，AI 最麻烦的不是笨，是乱。新开一个对话，它不知道上回做到哪了。更烦的是它会“记得”我根本没说过的事。我专门试过一次：第一轮它自己给场景定了个黄昏，换个对话，它就当成我的要求照着写了。还有写完自己说没问题的，还有付费生成点下去没反应、不知道扣没扣钱的。

这个仓库是我后来摸出来的办法，就两个 skill。

**multi-ai-handoff** 管分工。谁干活、谁检查、谁拍板，先说清楚。交接只看文件，交之前换个 AI 查一遍。花钱的生成先记账再点。挑模型看活有多难，别什么都上最贵的。

**project-memory** 管记性。进度和规矩都写进项目文件夹，新对话读一遍文件就知道接着干啥。规则台账只记我亲口说过的，AI 猜的不算。

两个能分开装，一起用最好。中文在 `skills/zh/`，英文在 `skills/en/`，内容一样。

## 啥时候用得上

项目要做好几天、中间换好多次对话的，同时开好几个 AI 的，生成要花钱、返工心疼的，都用得上。只是问一两个问题的话，用不着。

## 我现在一直守着的几条

- 聊天记录不算数，写进文件的才算。
- 谁写的谁不能自己说过，得换个 AI 查。查完记下文件哈希，文件一改，之前那个“通过”就不作数了。
- 花钱和拍板只有我能做。付费的先记一笔，只点一次。点完拿不准成没成，先去平台上看，别急着再点。
- 挑模型前先给活打个分：`S = 2N + 2K + A + F − 2E`。贵的模型留给真要动脑的活。
- 规矩只抄我的原话。

## 30 秒看一下

上一次点了但不知道成没成，账本就不让你再点：

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

**Claude Code**：把要用的 skill 文件夹复制到 `~/.claude/skills/`（全局）或者项目里的 `.claude/skills/`。

```bash
git clone https://github.com/xuyewild/multi-ai-skills
cp -r multi-ai-skills/skills/zh/multi-ai-handoff ~/.claude/skills/
cp -r multi-ai-skills/skills/zh/project-memory ~/.claude/skills/
```

想用分档的子 agent，把 `skills/zh/multi-ai-handoff/templates/tier-agents/` 和 `templates/independent-reviewer.md` 复制到项目的 `.claude/agents/`。

**Claude 网页版或桌面版**：把 skill 文件夹打成 zip，在设置里上传成自定义 skill。

**其他 AI**：skill 就是几份 Markdown 加几个 Python 脚本，把 `SKILL.md` 和它提到的参考文件丢给它读就行。

## 脚本

只用 Python 标准库，3.9 以上就能跑。

| 脚本 | 做什么 |
|---|---|
| `multi-ai-handoff/scripts/review_gate.py` | 记下复核结论和文件哈希，交接前查一下能不能放行 |
| `multi-ai-handoff/scripts/ledger.py` | 付费操作的账本：管预算、管重试次数，状态不明就不让再点 |
| `project-memory/scripts/check_project.py` | 检查规则台账的格式和项目里的关键文件 |

```bash
python -m unittest discover -s tests -v
```

## 反馈

有问题直接开 issue，最好是你在自己项目里真用过之后碰到的。想改哪条规矩，说说当时在做什么、出了什么岔子。

## 许可证

[MIT](LICENSE)
