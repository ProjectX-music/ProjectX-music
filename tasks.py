# Jukebox Tasks
import inspect
import os
import pathlib

import psutil
from invoke import task, Context

# https://github.com/pyinvoke/invoke/issues/833 (temporary-fix)
# https://github.com/pyinvoke/invoke/issues/357#issuecomment-428251193 (temporary-fix)
inspect.getargspec = inspect.getfullargspec

root_dir = pathlib.Path(__file__).parent
migrations_root = root_dir / 'migrations'


# //-------------------- migrations --------------------

@task
def makemigration(ctx: Context, message: str = None, scriptable: bool = False) -> None:
    """Create a new db migration script"""
    if not message:
        message = input("Please describe your migration: ")

    # configure
    options = f"--no-config-file --batch --message '{message}'"
    if not scriptable:
        options += " --sql"

    # execute
    ctx.run(f"yoyo new {options} {migrations_root}")


@task
def migrate(ctx: Context, develop: bool = False) -> None:
    """Run pre-start tasks including db migrations"""
    database = "postgresql://postgres:postgres@localhost:5432/jukebox_db"

    # configure
    options = f"--no-config-file --batch --database {database}"
    verbose_mode = "-vv"

    operation = "apply"
    if develop:
        operation = "develop"

    # execute
    ctx.run(f"yoyo list {options} {migrations_root}")
    print()
    ctx.run(f"yoyo {operation} {options} {verbose_mode} {migrations_root}")


# //-------------------- server --------------------

@task(help={'prod': 'run server in production mode'})
def runserver(ctx: Context, prod=False) -> None:
    """Starts the JukeBox API server"""
    # change current working directory to project root
    os.chdir(root_dir)

    # configure server
    if prod and not psutil.WINDOWS:
        start_cmd = "gunicorn -c gunicorn.conf.py backend.main:app"
    else:
        start_cmd = "uvicorn backend.main:app --reload"

    # run server
    ctx.run(start_cmd)