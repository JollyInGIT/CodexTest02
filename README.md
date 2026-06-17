# Industrial Document Search

一个面向工业仪器说明书的 Python 文档搜索引擎原型，采用 **Document Search + Citation + LLM** 架构：

- 管理员导入仪器说明书，形成可审计的底层参考数据。
- 工程师按仪器、型号或指定文档范围查询使用/开发问题。
- 检索采用 BM25 词法相关性 + TF-IDF 语义近似的混合排序，而不是单纯向量检索。
- 返回结果包含文档标题、页码和证据片段；不确定时返回候选文档范围，避免强行编造答案。
- LLM 仅用于基于证据的解释，不负责无依据生成。

## 快速开始

```bash
python -m industrial_doc_search.cli --store data/manual_index.json ingest sample_docs/pressure_tx_3000.txt \
  --document-id pressure-tx-3000 --title "Pressure TX-3000 Manual" --instrument pressure_transmitter --model TX-3000

python -m industrial_doc_search.cli --store data/manual_index.json search "如何校准零点" \
  --instrument pressure_transmitter --model TX-3000
```

## 推荐生产架构

1. 文档输入：PDF 解析、OCR、页码保留、型号/仪器元数据标注。
2. 索引层：按文档和型号隔离分区；混合检索可替换为 Elasticsearch/OpenSearch BM25 + 向量库。
3. 证据层：所有结果保留页码、文档 ID、修订版本和片段。
4. LLM 层：只接收检索证据；提示词要求“证据不足则说明不确定”。
5. 审计层：记录查询、命中文档、回答和引用，便于追溯工程判断。
