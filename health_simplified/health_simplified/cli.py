import typer
from datetime import date
from typing import Optional
from .database import get_db
from .models import User, FoodEntry

app = typer.Typer()

@app.command()
def user_create(name: str):
    """Create a new user"""
    db = next(get_db())
    user = User.create(db, name)
    typer.echo(f"Created user: {user.name} (ID: {user.id})")

@app.command()
def user_list():
    """List all users"""
    db = next(get_db())
    users = User.get_all(db)
    if not users:
        typer.echo("No users found")
        return
    
    typer.echo("Users:")
    for user in users:
        typer.echo(f"- {user.name} (ID: {user.id})")

@app.command()
def entry_add(
    user: str,
    food: str,
    calories: int,
    entry_date: Optional[str] = typer.Option(None, "--date", "-d"),
):
    """Add a food entry"""
    db = next(get_db())
    user_obj = User.get_by_name(db, user)
    if not user_obj:
        typer.echo(f"User '{user}' not found")
        raise typer.Exit(1)
    
    entry_date = entry_date or date.today().isoformat()
    entry = FoodEntry.create(db, user_obj.id, food, calories, entry_date)
    typer.echo(f"Added entry: {entry.food} ({entry.calories} kcal) on {entry.date}")

@app.command()
def entry_list(
    user: Optional[str] = typer.Option(None, "--user", "-u"),
    entry_date: Optional[str] = typer.Option(None, "--date", "-d"),
):
    """List food entries"""
    db = next(get_db())
    user_obj = None
    if user:
        user_obj = User.get_by_name(db, user)
        if not user_obj:
            typer.echo(f"User '{user}' not found")
            raise typer.Exit(1)
    
    entries = FoodEntry.get_all(db, user_obj.id if user_obj else None, entry_date)
    if not entries:
        typer.echo("No entries found")
        return
    
    typer.echo("Food Entries:")
    for entry in entries:
        user_name = User.get_by_name(db, entry.user_id).name if not user_obj else user_obj.name
        typer.echo(
            f"- ID: {entry.id}, User: {user_name}, Food: {entry.food}, "
            f"Calories: {entry.calories}, Date: {entry.date}"
        )

if __name__ == "__main__":
    app()