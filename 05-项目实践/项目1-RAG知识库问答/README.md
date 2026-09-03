# 项目 1：RAG 知识库问答

> 一个完整、可评测、可部署的 RAG 知识库问答系统，作为 Agent 应用岗和算法岗的共同作品集项目。
> 领域：法规 / 合规（中国金融 / 资本市场监管 + 上市公司公告，公开数据）。
> 执行计划与动态调整见 `计划.md`；优化细节见 `../RAG优化学习与应用路线.md`。

## 一句话

用户提问 → 系统从知识库检索相关资料 → 生成带引用的回答。

## 成功指标

- 自建 50 条测试问答，回答准确率 ≥ 80%
- 每条回答都能溯源到文档引用
- 查询接口 P95 延迟 < 3 秒
- 能用 `docker compose up` 一键启动
- 至少完成 1 轮 Bad Case 修复并记录对比

## 系统链路

```
文档 → 清洗 → 分块 → Embedding → 向量库
                                      ↓
用户提问 → 意图理解 → 混合检索 → 重排 → LLM 生成 → 引用溯源
```

## 技术栈（目标）

- 后端：FastAPI
- 向量库：Chroma（熟悉后可换 Milvus / pgvector）
- 框架：LangChain
- 模型：Embedding + 一个 LLM API（Qwen / DeepSeek / OpenAI 兼容）
- 部署：Docker Compose
- 评测：RAGAS + 人工标注集

## 目录结构

```
项目1-RAG知识库问答/
├── scripts/
│   └── data_prep.py        # M1：清洗 + 分块，比较 chunk size
├── data/
│   ├── docs/               # 放原始文档（txt/md）
│   ├── cleaned.json        # 清洗后（脚本生成）
│   └── chunks_*.json       # 分块结果（脚本生成）
├── app/                    # M2+：FastAPI 服务与检索链路
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 快速开始（当前 M1）

```bash
# 1. 安装依赖（M1 只需 langchain-text-splitters）
pip install -r requirements.txt

# 2. 把文档放进 data/docs/（txt / md 均可）

# 3. 清洗 + 分块，比较不同 chunk size
python scripts/data_prep.py --sizes 300 500 800
```

## 里程碑

- [x] M1 数据准备：清洗 + 分块 + chunk size 对比
- [ ] M2 向量检索：选 Embedding、建向量库、跑召回
- [ ] M3 完整问答：检索 → 重排 → 生成 → 引用 + 混合检索
- [ ] M4 评测：自建 50 条问答，RAGAS 评测
- [ ] M5 部署：FastAPI + Docker Compose
- [ ] M6 迭代：Bad Case 修复一轮并记录对比

## 面试叙事

1 分钟：这是一个知识库问答系统，用 RAG 解决模型不知道私有知识的问题，支持混合检索和引用溯源，50 条评测准确率 80%+，Bad Case 分析后把某类问题从 X% 提升到 Z%。

5 分钟：按「业务 → 数据 → 分块 → 检索 → 重排 → 生成 → 评测 → 部署 → 迭代」讲，每个环节说清选择和替代方案。
