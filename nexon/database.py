"""
nexon.dataManager
~~~~~~~~~~~~~~~~

A unified data management system for handling JSON data storage.

:copyright: (c) 2024 Mahirox36
:license: MIT, see LICENSE for more details.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from collections import OrderedDict
from time import time
from typing import TYPE_CHECKING, Any, Dict, List, NoReturn, Optional, Union

from tortoise import Tortoise, connections

if TYPE_CHECKING:
    from typing_extensions import Self

__all__ = (
    "DataManager",
    "init_db",
    "close_db",
)


async def init_db(
    username: Optional[str],
    password: Optional[str],
    host: Optional[str],
    port: int = 5432,
    db_name: str = "bot",
    database: str = "postgres"
    ) -> None:
    if database == "sqlite":
        db_name = f"{db_name}.sqlite3"
    else:
        if not username or not password or not host:
            raise ValueError(f"Username, password, and host are required for {database or "PostgreSQL"}.")
        db_name = f"{username}:{password}@{host}:{port}/{db_name}"
    await Tortoise.init(
        db_url=f"{database}://{db_name}", #"sqlite://db.sqlite3",
        modules={"models": ["nexon.data.models"]},
    )
    await Tortoise.generate_schemas()

async def close_db():
    await connections.close_all()

class DataManager:
    """
    Database using postgresSQL
    """
    def __init__(self):
        pass