from typer.testing import CliRunner
from health_simplified.cli.main import app
import pytest
import uuid

runner = CliRunner()

@pytest.fixture
def runner_instance():
    return runner

def test_user_create(runner_instance, test_db):
    unique_name = f"TestUser_{uuid.uuid4().hex[:6]}"
    result = runner_instance.invoke(app, ["user create", unique_name])
    assert result.exit_code == 0, f"Error: {result.stdout}"
    assert "Created user" in result.stdout

def test_entry_add_invalid_calories(runner_instance, test_db):
    unique_name = f"CalorieUser_{uuid.uuid4().hex[:6]}"
    create_result = runner_instance.invoke(app, ["user create", unique_name])
    assert create_result.exit_code == 0, f"User create failed: {create_result.stdout}"

   
    result = runner_instance.invoke(app, ["entry add", unique_name, "Apple", "--", "-100"])
    assert result.exit_code == 1
    assert "positive" in result.stdout
