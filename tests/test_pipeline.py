import pytest
from unittest.mock import AsyncMock, patch
from orchestrator.pipeline import UnifiedPipeline

@pytest.mark.asyncio
async def test_pipeline_council_mocked():
    with patch("orchestrator.pipeline.GeminiRouter") as mock_router_cls:
        mock_router = mock_router_cls.return_value
        
        # 10 Round 1 briefs
        round_1_briefs = [
            f"directives:\n  - directive {i}\nconstraints:\n  - const {i}\nred_flags:\n  - risk {i}"
            for i in range(1, 11)
        ]
        # 10 Round 2 debates
        round_2_debates = [
            f"endorse:\n  - e{i}\nobjection:\n  - o{i}\nconsensus_vote:\n  - v{i}"
            for i in range(1, 11)
        ]
        
        mock_router.request = AsyncMock(side_effect=[
            *round_1_briefs,
            *round_2_debates,
            # Round 3 synthesis blueprint
            "# Master Architecture Blueprint\nTest content",
            # Learner distillation
            "learnings:\n  - scope: project\n    target: current_project\n    rule: Test Rule",
        ])
        
        pipeline = UnifiedPipeline(router=mock_router)
        res = await pipeline.run(task="Test user dashboard", mode="council")
        
        assert res["status"] == "success"
        assert "blueprint" in res
        assert "# Master Architecture Blueprint" in res["blueprint"]
        assert len(res["briefs"]) == 10
        assert len(res["debates"]) == 10
        assert len(res["learnings"]) >= 1
