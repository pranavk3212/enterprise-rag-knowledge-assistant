from enterprise_rag.cli import _has_inline_expected_source_citation
from enterprise_rag.schemas import Chunk
from enterprise_rag.service import EnterpriseRAG


def test_source_list_includes_each_retrieved_chunk():
    sources = [
        Chunk("policy.md:1", "Policy text", "policy.md", 1),
        Chunk("other.md:2", "Other text", "other.md", 2),
    ]
    answer = EnterpriseRAG._with_source_list("A cited answer.", sources)
    assert "Sources: [policy.md · chunk 1] [other.md · chunk 2]" in answer


def test_inline_expected_source_citation_is_counted():
    answer = (
        "Employees receive the stated benefit [benefits.md · chunk 2]."
        "\n\nSources: [benefits.md · chunk 2] [remote_work.md · chunk 1]"
    )
    assert _has_inline_expected_source_citation(answer, "benefits.md")


def test_source_footer_alone_does_not_count_as_inline_citation():
    answer = (
        "Employees receive the stated benefit, according to the retrieved text."
        "\n\nSources: [benefits.md · chunk 2] [remote_work.md · chunk 1]"
    )
    assert not _has_inline_expected_source_citation(answer, "benefits.md")


def test_unrelated_inline_citation_does_not_count_for_expected_source():
    answer = (
        "Employees receive the stated benefit [remote_work.md · chunk 1]."
        "\n\nSources: [benefits.md · chunk 2] [remote_work.md · chunk 1]"
    )
    assert not _has_inline_expected_source_citation(answer, "benefits.md")
