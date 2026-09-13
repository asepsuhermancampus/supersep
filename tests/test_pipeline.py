import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from orchestrator.pipeline import UnifiedPipeline

@pytest.mark.asyncio
async def test_pipeline_council_mocked():
    with patch("orchestrator.pipeline.GeminiRouter") as mock_router_cls:
        mock_router = mock_router_cls.return_value
        mock_router.request = AsyncMock(side_effect=[
            # 5 Round 1 briefs
            "directives:\n  - directive 1\nconstraints:\n  - const 1\nred_flags:\n  - risk 1",
            "directives:\n  - directive 2\nconstraints:\n  - const 2\nred_flags:\n  - risk 2",
            "directives:\n  - directive 3\nconstraints:\n  - const 3\nred_flags:\n  - risk 3",
            "directives:\n  - directive 4\nconstraints:\n  - const 4\nred_flags:\n  - risk 4",
            "directives:\n  - directive 5\nconstraints:\n  - const 5\nred_flags:\n  - risk 5",
            # 5 Round 2 debates
            "endorse:\n  - e1\nobjection:\n  - o1\nconsensus_vote:\n  - v1",
            "endorse:\n  - e2\nobjection:\n  - o2\nconsensus_vote:\n  - v2",
            "endorse:\n  - e3\nobjection:\n  - o3\nconsensus_vote:\n  - v3",
            "endorse:\n  - e4\nobjection:\n  - o4\nconsensus_vote:\n  - v4",
            "endorse:\n  - e5\nobjection:\n  - o5\nconsensus_vote:\n  - v5",
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
        assert len(res["briefs"]) == 5
        assert len(res["debates"]) == 5
        assert len(res["learnings"]) >= 1
