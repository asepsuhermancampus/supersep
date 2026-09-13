import pytest
from unittest.mock import AsyncMock, MagicMock
from orchestrator.assembly import AssemblyLine

@pytest.mark.asyncio
async def test_assembly_line_structure():
    mock_router = MagicMock()
    mock_router.request = AsyncMock(return_value="OK")
    assembly = AssemblyLine(router=mock_router)
    
    ui_spec = await assembly.generate_ui_spec("blueprint test")
    assert ui_spec == "OK"

    data_spec = await assembly.generate_data_spec("blueprint test")
    assert data_spec == "OK"

    code = await assembly.implement_code("task test", ui_spec, data_spec)
    assert code == "OK"

    review = await assembly.adversarial_review(code, "task test")
    assert review["status"] == "success"
    assert "OK" in review["critique"]
