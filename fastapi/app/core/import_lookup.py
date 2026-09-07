"""Bounded import lookups shared by the independently packaged backends."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from itertools import islice
from typing import Any, TypeVar

IMPORT_QUERY_BATCH_SIZE = 500
T = TypeVar("T", str, int)


@dataclass
class ImportKeys:
    usernames: set[str] = field(default_factory=set)
    mobiles: set[str] = field(default_factory=set)
    departments: set[int] = field(default_factory=set)
    roles: set[int] = field(default_factory=set)


def collect_import_keys(
    rows: Iterable[tuple[Any, ...]],
    *,
    username: int,
    mobile: int | None,
    dept: int | None,
    role: int | None,
    default_dept: int | None,
) -> ImportKeys:
    """Collect references only; row validation still owns errors and fallback."""
    keys = ImportKeys()
    if default_dept is not None:
        keys.departments.add(default_dept)
    for row in rows:
        for index, target in ((username, keys.usernames), (mobile, keys.mobiles)):
            if index is not None and row[index]:
                value = str(row[index]).strip()
                if value:
                    target.add(value)
        if dept is not None and row[dept] is not None:
            try:
                keys.departments.add(int(row[dept]))
            except (TypeError, ValueError):
                pass
        if role is not None and row[role] is not None:
            try:
                keys.roles.update(int(value.strip()) for value in str(row[role]).split(",") if value.strip())
            except (TypeError, ValueError):
                pass
    return keys


def query_batches(values: Iterable[T]) -> Iterator[list[T]]:
    # Global ordering also keeps row-lock acquisition order stable across batches.
    iterator = iter(sorted(values))
    while batch := list(islice(iterator, IMPORT_QUERY_BATCH_SIZE)):
        yield batch
