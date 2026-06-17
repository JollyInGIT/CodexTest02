from industrial_doc_search import DocumentRecord, DocumentSearchEngine


def build_engine() -> DocumentSearchEngine:
    engine = DocumentSearchEngine()
    engine.add_document(
        DocumentRecord("tx3000", "TX-3000 Manual", "pressure", "TX-3000"),
        [
            "安装说明。供电电压为 24VDC。零点校准前应关闭过程阀。",
            "零点校准步骤：进入维护菜单，选择 Zero Trim，稳定后按 Confirm。",
        ],
    )
    engine.add_document(
        DocumentRecord("flow100", "FLOW-100 Manual", "flow", "FLOW-100"),
        ["FLOW-100 流量计量程设置在 Range 菜单完成。"],
    )
    return engine


def test_search_returns_citation_page() -> None:
    results = build_engine().search("Zero Trim 零点校准", instrument="pressure", model="TX-3000")
    assert results
    assert results[0].citation == "TX-3000 Manual, p.2"


def test_scope_prevents_cross_instrument_mixing() -> None:
    results = build_engine().search("Range", instrument="pressure", model="TX-3000")
    assert results == []


def test_uncertain_answer_returns_document_range() -> None:
    answer = build_engine().answer("校准", instrument="pressure", model="TX-3000")
    assert answer["status"] in {"confident", "uncertain"}
    assert answer["citations"]
