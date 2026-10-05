from enterprise_rag.loaders import recursive_chunks


def test_recursive_chunks_preserves_all_text_with_overlap():
    text = "alpha " * 400
    chunks = recursive_chunks(text, size=120, overlap=20)
    assert len(chunks) > 1
    assert chunks[0].startswith("alpha")
    assert chunks[-1].endswith("alpha")


def test_recursive_chunks_handles_empty_text():
    assert recursive_chunks("", size=100, overlap=10) == []
