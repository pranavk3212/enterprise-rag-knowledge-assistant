from enterprise_rag.schemas import Chunk
from enterprise_rag.service import EnterpriseRAG


def test_source_list_includes_each_retrieved_chunk():
    sources = [
        Chunk("policy.md:1", "Policy text", "policy.md", 1),
        Chunk("other.md:2", "Other text", "other.md", 2),
    ]
    answer = EnterpriseRAG._with_source_list("A cited answer.", sources)
    assert "Sources: [policy.md · chunk 1] [other.md · chunk 2]" in answer
