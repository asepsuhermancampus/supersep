import pytest
from orchestrator.council import Council

def test_build_lean_matrix():
    council = Council()
    mock_briefs = [
        {
            "agent_id": "agent_1",
            "directives": ["Direct A"],
            "constraints": ["Const A"],
            "red_flags": ["Risk A"],
        },
        {
            "agent_id": "agent_2",
            "directives": ["Direct B"],
            "constraints": ["Const B"],
            "red_flags": ["Risk B"],
        }
    ]
    matrix = council.build_lean_matrix(mock_briefs)
    assert "[agent_1]" in matrix
    assert "Direct A" in matrix
    assert "[agent_2]" in matrix
    assert len(matrix) < 2000  # Enforce lean token size
