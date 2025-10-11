"""
Integration tests for API endpoints with real database

These tests require a running PostgreSQL database with pgvector extension.
Run with: pytest -m integration
"""
import pytest
from unittest.mock import patch, MagicMock
from app.models import LegalTextDB, LegalText


@pytest.mark.integration
class TestHealthEndpoint:
    """Integration tests for health check endpoint"""

    def test_health_check(self, integration_client):
        """Test health check endpoint returns correct response"""
        response = integration_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.2.0"


@pytest.mark.integration
class TestGetAvailableCodesEndpoint:
    """Integration tests for GET /legal-texts/gesetze-im-internet/codes"""

    @pytest.mark.asyncio
    async def test_get_available_codes_empty_database(self, integration_client):
        """Test endpoint returns empty list when database is empty"""
        response = integration_client.get("/legal-texts/gesetze-im-internet/codes")

        assert response.status_code == 200
        data = response.json()
        assert data["codes"] == []

    @pytest.mark.asyncio
    async def test_get_available_codes_with_data(self, integration_client, test_repository):
        """Test endpoint returns codes from database"""
        # Add test data
        legal_texts = [
            LegalTextDB(
                text="Text 1",
                code="bgb",
                section="§ 1",
                sub_section="1",
                text_vector=[0.1] * 2560
            ),
            LegalTextDB(
                text="Text 2",
                code="stgb",
                section="§ 1",
                sub_section="1",
                text_vector=[0.2] * 2560
            ),
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Test endpoint
        response = integration_client.get("/legal-texts/gesetze-im-internet/codes")

        assert response.status_code == 200
        data = response.json()
        assert len(data["codes"]) == 2
        assert "bgb" in data["codes"]
        assert "stgb" in data["codes"]


@pytest.mark.integration
class TestGetLegalTextsEndpoint:
    """Integration tests for GET /legal-texts/gesetze-im-internet/{code}"""

    @pytest.mark.asyncio
    async def test_get_legal_texts_by_code(self, integration_client, test_repository):
        """Test getting legal texts by code"""
        # Add test data
        legal_texts = [
            LegalTextDB(
                text="BGB Text 1",
                code="bgb",
                section="§ 1",
                sub_section="1",
                text_vector=[0.1] * 2560
            ),
            LegalTextDB(
                text="BGB Text 2",
                code="bgb",
                section="§ 2",
                sub_section="1",
                text_vector=[0.2] * 2560
            ),
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Test endpoint
        response = integration_client.get("/legal-texts/gesetze-im-internet/bgb")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["results"]) == 2
        assert all(r["code"] == "bgb" for r in data["results"])

    @pytest.mark.asyncio
    async def test_get_legal_texts_with_section_filter(self, integration_client, test_repository):
        """Test getting legal texts filtered by section"""
        # Add test data
        legal_texts = [
            LegalTextDB(
                text="Section 1 text",
                code="bgb",
                section="§ 1",
                sub_section="1",
                text_vector=[0.1] * 2560
            ),
            LegalTextDB(
                text="Section 2 text",
                code="bgb",
                section="§ 2",
                sub_section="1",
                text_vector=[0.2] * 2560
            ),
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Test endpoint with section filter
        response = integration_client.get("/legal-texts/gesetze-im-internet/bgb?section=§ 1")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["section"] == "§ 1"
        assert data["results"][0]["text"] == "Section 1 text"

    @pytest.mark.asyncio
    async def test_get_legal_texts_not_found(self, integration_client):
        """Test 404 when no texts found"""
        response = integration_client.get("/legal-texts/gesetze-im-internet/nonexistent")

        assert response.status_code == 404
        assert "No legal texts found" in response.json()["detail"]

    def test_get_legal_texts_invalid_sub_section_without_section(self, integration_client):
        """Test 400 error when sub_section provided without section"""
        response = integration_client.get("/legal-texts/gesetze-im-internet/bgb?sub_section=1")

        assert response.status_code == 400
        assert "sub_section filter can only be used when section filter is also provided" in response.json()["detail"]


@pytest.mark.integration
class TestSemanticSearchEndpoint:
    """Integration tests for GET /legal-texts/gesetze-im-internet/{code}/search"""

    @pytest.mark.asyncio
    async def test_semantic_search_with_mocked_embeddings(self, integration_client, test_repository):
        """Test semantic search with mocked embedding service"""
        # Add test data with known embeddings
        legal_texts = [
            LegalTextDB(
                text="Contract law provisions",
                code="bgb",
                section="§ 1",
                sub_section="1",
                text_vector=[0.5] * 2560
            ),
            LegalTextDB(
                text="Property law provisions",
                code="bgb",
                section="§ 2",
                sub_section="1",
                text_vector=[0.9] * 2560
            ),
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Mock the embedding service to return a known embedding
        with patch('app.routers.legal_texts.get_embedding_service_dependency') as mock_service:
            mock_embedding = MagicMock()
            mock_embedding.generate_embeddings = MagicMock(return_value=[[0.52] * 2560])
            mock_service.return_value = mock_embedding

            # Test endpoint
            response = integration_client.get("/legal-texts/gesetze-im-internet/bgb/search?q=contract")

            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "contract"
            assert data["code"] == "bgb"
            assert data["count"] >= 1
            # First result should be most similar
            assert data["results"][0]["text"] == "Contract law provisions"

    @pytest.mark.asyncio
    async def test_semantic_search_with_limit(self, integration_client, test_repository):
        """Test semantic search respects limit parameter"""
        # Add multiple texts
        legal_texts = [
            LegalTextDB(
                text=f"Text {i}",
                code="bgb",
                section=f"§ {i}",
                sub_section="1",
                text_vector=[float(i) / 100] * 2560
            )
            for i in range(10)
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Mock embedding service
        with patch('app.routers.legal_texts.get_embedding_service_dependency') as mock_service:
            mock_embedding = MagicMock()
            mock_embedding.generate_embeddings = MagicMock(return_value=[[0.05] * 2560])
            mock_service.return_value = mock_embedding

            # Test with limit=3
            response = integration_client.get("/legal-texts/gesetze-im-internet/bgb/search?q=test&limit=3")

            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 3
            assert len(data["results"]) == 3

    @pytest.mark.asyncio
    async def test_semantic_search_with_cutoff(self, integration_client, test_repository):
        """Test semantic search with cutoff parameter"""
        # Add texts with different embeddings
        legal_texts = [
            LegalTextDB(
                text="Very similar text",
                code="bgb",
                section="§ 1",
                sub_section="1",
                text_vector=[0.5] * 2560
            ),
            LegalTextDB(
                text="Very different text",
                code="bgb",
                section="§ 2",
                sub_section="1",
                text_vector=[0.99] * 2560
            ),
        ]
        await test_repository.add_legal_texts_batch(legal_texts)

        # Mock embedding service
        with patch('app.routers.legal_texts.get_embedding_service_dependency') as mock_service:
            mock_embedding = MagicMock()
            mock_embedding.generate_embeddings = MagicMock(return_value=[[0.5] * 2560])
            mock_service.return_value = mock_embedding

            # Test with strict cutoff
            response = integration_client.get("/legal-texts/gesetze-im-internet/bgb/search?q=test&cutoff=0.1")

            assert response.status_code == 200
            data = response.json()
            # Should only return very similar text
            assert data["count"] >= 1
            assert data["results"][0]["text"] == "Very similar text"


@pytest.mark.integration
class TestImportLegalTextEndpoint:
    """Integration tests for POST /legal-texts/gesetze-im-internet/{book}"""

    @pytest.mark.asyncio
    async def test_import_legal_text_success(self, integration_client, test_repository):
        """Test successful import of legal texts"""
        # Mock the scraper and embedding service
        legal_texts = [
            LegalText(text="Imported text 1", code="test_import", section="§ 1", sub_section="1"),
            LegalText(text="Imported text 2", code="test_import", section="§ 2", sub_section="1"),
        ]

        with patch('app.routers.legal_texts.GesetzteImInternetScraper') as mock_scraper_class, \
             patch('app.routers.legal_texts.get_embedding_service_dependency') as mock_embedding_service:

            # Setup scraper mock
            mock_scraper = MagicMock()
            mock_scraper.scrape.return_value = legal_texts
            mock_scraper_class.return_value = mock_scraper

            # Setup embedding service mock
            mock_embedding = MagicMock()
            mock_embedding.generate_embeddings = MagicMock(
                return_value=[[0.1] * 2560, [0.2] * 2560]
            )
            mock_embedding_service.return_value = mock_embedding

            # Test endpoint
            response = integration_client.post("/legal-texts/gesetze-im-internet/test_import")

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == "test_import"
            assert data["texts_imported"] == 2
            assert "Successfully imported" in data["message"]

            # Verify texts were actually saved to database
            from app.repository import LegalTextFilter
            filter = LegalTextFilter(code="test_import")
            results = await test_repository.get_legal_text(filter)
            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_import_updates_existing_texts(self, integration_client, test_repository):
        """Test that re-importing updates existing texts"""
        # Add initial text
        initial_text = LegalTextDB(
            text="Original text",
            code="reimport_test",
            section="§ 1",
            sub_section="1",
            text_vector=[0.1] * 2560
        )
        await test_repository.add_legal_text(initial_text)

        # Mock scraper with updated text
        updated_texts = [
            LegalText(text="Updated text", code="reimport_test", section="§ 1", sub_section="1"),
        ]

        with patch('app.routers.legal_texts.GesetzteImInternetScraper') as mock_scraper_class, \
             patch('app.routers.legal_texts.get_embedding_service_dependency') as mock_embedding_service:

            mock_scraper = MagicMock()
            mock_scraper.scrape.return_value = updated_texts
            mock_scraper_class.return_value = mock_scraper

            mock_embedding = MagicMock()
            mock_embedding.generate_embeddings = MagicMock(return_value=[[0.2] * 2560])
            mock_embedding_service.return_value = mock_embedding

            # Import again
            response = integration_client.post("/legal-texts/gesetze-im-internet/reimport_test")

            assert response.status_code == 200

            # Verify text was updated, not duplicated
            from app.repository import LegalTextFilter
            filter = LegalTextFilter(code="reimport_test")
            results = await test_repository.get_legal_text(filter)
            assert len(results) == 1
            assert results[0].text == "Updated text"
