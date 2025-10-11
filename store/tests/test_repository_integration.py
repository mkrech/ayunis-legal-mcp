"""
Integration tests for LegalTextRepository with real database

These tests require a running PostgreSQL database with pgvector extension.
Run with: pytest -m integration
"""
import pytest
from app.repository import LegalTextFilter
from app.models import LegalTextDB


@pytest.mark.integration
class TestLegalTextRepositoryIntegration:
    """Integration tests for repository with real database"""

    @pytest.mark.asyncio
    async def test_add_and_retrieve_legal_text(self, test_repository):
        """Test adding a legal text and retrieving it"""
        # Add legal text
        legal_text = LegalTextDB(
            text="Test legal text content",
            code="test_code",
            section="§ 1",
            sub_section="1",
            text_vector=[0.1] * 2560
        )
        added = await test_repository.add_legal_text(legal_text)

        assert added.id is not None
        assert added.text == "Test legal text content"
        assert added.code == "test_code"

        # Retrieve it
        filter = LegalTextFilter(code="test_code")
        results = await test_repository.get_legal_text(filter)

        assert len(results) == 1
        assert results[0].text == "Test legal text content"

    @pytest.mark.asyncio
    async def test_add_legal_texts_batch(self, test_repository):
        """Test batch adding legal texts"""
        legal_texts = [
            LegalTextDB(
                text=f"Text {i}",
                code="batch_test",
                section=f"§ {i}",
                sub_section="1",
                text_vector=[float(i) / 100] * 2560
            )
            for i in range(5)
        ]

        await test_repository.add_legal_texts_batch(legal_texts)

        # Verify all were added
        filter = LegalTextFilter(code="batch_test")
        results = await test_repository.get_legal_text(filter)

        assert len(results) == 5
        assert all(r.code == "batch_test" for r in results)

    @pytest.mark.asyncio
    async def test_upsert_updates_existing_legal_text(self, test_repository):
        """Test that batch upsert updates existing records"""
        # Add initial record
        legal_text = LegalTextDB(
            text="Original text",
            code="upsert_test",
            section="§ 1",
            sub_section="1",
            text_vector=[0.1] * 2560
        )
        await test_repository.add_legal_text(legal_text)

        # Upsert with same code/section/sub_section but different text
        updated_text = LegalTextDB(
            text="Updated text",
            code="upsert_test",
            section="§ 1",
            sub_section="1",
            text_vector=[0.2] * 2560
        )
        await test_repository.add_legal_texts_batch([updated_text])

        # Verify it was updated, not duplicated
        filter = LegalTextFilter(code="upsert_test")
        results = await test_repository.get_legal_text(filter)

        assert len(results) == 1
        assert results[0].text == "Updated text"

    @pytest.mark.asyncio
    async def test_filter_by_section(self, test_repository):
        """Test filtering legal texts by section"""
        # Add multiple texts
        legal_texts = [
            LegalTextDB(
                text="Section 1 text",
                code="filter_test",
                section="§ 1",
                sub_section="1",
                text_vector=[0.1] * 2560
            ),
            LegalTextDB(
                text="Section 2 text",
                code="filter_test",
                section="§ 2",
                sub_section="1",
                text_vector=[0.2] * 2560
            ),
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Filter by section
        filter = LegalTextFilter(code="filter_test", section="§ 1")
        results = await test_repository.get_legal_text(filter)

        assert len(results) == 1
        assert results[0].section == "§ 1"
        assert results[0].text == "Section 1 text"

    @pytest.mark.asyncio
    async def test_filter_by_sub_section(self, test_repository):
        """Test filtering legal texts by sub-section"""
        # Add multiple texts with different sub-sections
        legal_texts = [
            LegalTextDB(
                text="Sub-section 1",
                code="subsection_test",
                section="§ 1",
                sub_section="1",
                text_vector=[0.1] * 2560
            ),
            LegalTextDB(
                text="Sub-section 2",
                code="subsection_test",
                section="§ 1",
                sub_section="2",
                text_vector=[0.2] * 2560
            ),
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Filter by sub-section
        filter = LegalTextFilter(code="subsection_test", section="§ 1", sub_section="2")
        results = await test_repository.get_legal_text(filter)

        assert len(results) == 1
        assert results[0].sub_section == "2"
        assert results[0].text == "Sub-section 2"

    @pytest.mark.asyncio
    async def test_count_by_code(self, test_repository):
        """Test counting legal texts by code"""
        # Add multiple texts
        legal_texts = [
            LegalTextDB(
                text=f"Text {i}",
                code="count_test",
                section=f"§ {i}",
                sub_section="1",
                text_vector=[float(i) / 100] * 2560
            )
            for i in range(3)
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Count
        count = await test_repository.count_by_code("count_test")
        assert count == 3

    @pytest.mark.asyncio
    async def test_get_available_codes(self, test_repository):
        """Test getting list of available codes"""
        # Add texts with different codes
        legal_texts = [
            LegalTextDB(
                text="Text 1",
                code="code_a",
                section="§ 1",
                sub_section="1",
                text_vector=[0.1] * 2560
            ),
            LegalTextDB(
                text="Text 2",
                code="code_b",
                section="§ 1",
                sub_section="1",
                text_vector=[0.2] * 2560
            ),
            LegalTextDB(
                text="Text 3",
                code="code_a",
                section="§ 2",
                sub_section="1",
                text_vector=[0.3] * 2560
            ),
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Get available codes
        codes = await test_repository.get_available_codes()

        assert len(codes) == 2
        assert "code_a" in codes
        assert "code_b" in codes

    @pytest.mark.asyncio
    async def test_semantic_search_finds_similar_texts(self, test_repository):
        """Test semantic search with real database"""
        # Add texts with different embeddings
        legal_texts = [
            LegalTextDB(
                text="Contract law text",
                code="search_test",
                section="§ 1",
                sub_section="1",
                text_vector=[0.5] * 2560  # Similar to query
            ),
            LegalTextDB(
                text="Criminal law text",
                code="search_test",
                section="§ 2",
                sub_section="1",
                text_vector=[0.9] * 2560  # Less similar to query
            ),
            LegalTextDB(
                text="Property law text",
                code="search_test",
                section="§ 3",
                sub_section="1",
                text_vector=[0.1] * 2560  # Very different from query
            ),
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Search with query embedding close to [0.5] * 2560
        query_embedding = [0.52] * 2560
        results = await test_repository.semantic_search(
            query_embedding=query_embedding,
            code="search_test",
            limit=10
        )

        # Verify results are ordered by similarity
        assert len(results) == 3
        # First result should be most similar (closest to 0.5)
        assert results[0][0].text == "Contract law text"
        # Check distances are ascending
        assert results[0][1] < results[1][1] < results[2][1]

    @pytest.mark.asyncio
    async def test_semantic_search_with_cutoff(self, test_repository):
        """Test semantic search with cutoff threshold"""
        # Add texts with very different embeddings
        legal_texts = [
            LegalTextDB(
                text="Similar text",
                code="cutoff_test",
                section="§ 1",
                sub_section="1",
                text_vector=[0.5] * 2560
            ),
            LegalTextDB(
                text="Dissimilar text",
                code="cutoff_test",
                section="§ 2",
                sub_section="1",
                text_vector=[0.99] * 2560
            ),
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Search with a strict cutoff
        query_embedding = [0.5] * 2560
        results = await test_repository.semantic_search(
            query_embedding=query_embedding,
            code="cutoff_test",
            limit=10,
            cutoff=0.1  # Very strict cutoff
        )

        # Should only return the similar text
        assert len(results) == 1
        assert results[0][0].text == "Similar text"

    @pytest.mark.asyncio
    async def test_semantic_search_respects_limit(self, test_repository):
        """Test that semantic search respects the limit parameter"""
        # Add multiple texts
        legal_texts = [
            LegalTextDB(
                text=f"Text {i}",
                code="limit_test",
                section=f"§ {i}",
                sub_section="1",
                text_vector=[float(i) / 100] * 2560
            )
            for i in range(10)
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Search with limit of 3
        query_embedding = [0.05] * 2560
        results = await test_repository.semantic_search(
            query_embedding=query_embedding,
            code="limit_test",
            limit=3
        )

        assert len(results) == 3
