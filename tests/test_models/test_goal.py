from typer.testing import CliRunner
from health_simplified.cli.main import app
import pytest
import uuid

runner = CliRunner()

def test_goal_set_and_show(test_db):
    # Use a unique username to avoid conflict
    user_name = f"GoalUser_{uuid.uuid4().hex[:6]}"

    # Create test user
    result_create = runner.invoke(app, ["user create", user_name])
    assert result_create.exit_code == 0, f"Create failed: {result_create.stdout}"

    # Set goal
    result_set = runner.invoke(app, ["goal set", user_name, "2000", "14000"])
    assert result_set.exit_code == 0, f"Set goal failed: {result_set.stdout}"

    # Show goal
    result_show = runner.invoke(app, ["goal show", user_name])
    assert result_show.exit_code == 0, f"Show goal failed: {result_show.stdout}"
    assert f"Nutrition Goals for {user_name}" in result_show.stdout
    assert "2000 kcal" in result_show.stdout
