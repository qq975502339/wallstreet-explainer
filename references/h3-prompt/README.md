# H3 提示词编写（vendored 自 OpenMontage h3-prompt-writing）

`SKILL.md` 为技能原文（模式判定与输出规则）；`base-en.txt` / `ref-en.txt` 与源仓库逐字节一致（已校验）。本 README 只是索引。

给 AutoDL H3 工作流写/改提示词前**必读**对应参考文件，不可凭记忆套通用提示词：

| 输入模式 | 读 | 结构 |
|---|---|---|
| T2VA / I2VA / FL2VA / L2VA（纯文本/首帧/首末帧/末帧） | `base-en.txt` | `integrated_multimodal_description` → `overall_soundscape` → `non_diegetic_music`，顺序不变 |
| Ref2VA（完整参考图+参考音频，数字主持人走这条） | `ref-en.txt` | `subject_definitions` → `summary` → `retention_analysis` → `detailed_description` → `overall_soundscape` → `non_diegetic_music`，六段顺序不变 |

规则：
- 改写段落用英文；**口播台词、歌词、画面可见文字保持原语言（中文口播保持中文）**。
- 参考标签（`<Picture 1>`/`<Audio 1>` 等）全篇一致，且与实际传入素材一一对应；不提供的素材不得虚构标签。
- 描述总时长与请求时长（4–15 秒）匹配；逐镜写构图/主体/环境/动作/镜头/声音/参考内容出现时点。
- 不写剧情摘要、不留未解析标签；少用 "cinematic/beautiful" 这类空词，写具体视听细节。
- 数字主持人 additionally：把 `references/ai-presenter.md`「口播镜头硬约束」的镜头/人体禁止项**逐条**写进 prompt。

来源：qq975502339/OpenMontage `.agents/skills/h3-prompt-writing/`（SKILL.md + references）。