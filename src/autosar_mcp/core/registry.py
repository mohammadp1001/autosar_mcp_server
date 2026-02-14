"""In-memory object registry used to map stable IDs to Python objects.

This is used by the server layer to avoid sending raw Python objects across the
tool boundary; tools exchange IDs instead.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import uuid


@dataclass
class ObjectRegistry:
    """Stores arbitrary objects keyed by generated IDs."""

    _store: dict[str, Any] = field(default_factory=dict)

    def put(self, obj: Any, prefix: str) -> str:
        """Stores an object and returns its generated ID.

        Args:
            obj: Object instance to store.
            prefix: Prefix used to group IDs by type (e.g. "ws").

        Returns:
            Generated object ID.
        """
        oid = f"{prefix}_{uuid.uuid4().hex}"
        self._store[oid] = obj
        return oid

    def get(
        self, oid: str, expected_type: type | tuple[type, ...] | None = None
    ) -> Any:
        """Retrieves a stored object by ID, optionally enforcing its type.

        Args:
            oid: Object ID previously returned by :meth:`put`.
            expected_type: Optional type (or tuple of types) the object must be.

        Returns:
            The stored object.

        Raises:
            KeyError: If the object ID does not exist.
            TypeError: If ``expected_type`` is provided and the object is not an instance of it.
        """
        if oid not in self._store:
            raise KeyError(f"Unknown id: {oid}")
        obj = self._store[oid]
        if expected_type is not None and not isinstance(obj, expected_type):
            raise TypeError(f"{oid} is {type(obj)}, expected {expected_type}")
        return obj

    def delete(self, oid: str) -> None:
        """Deletes an object by ID.

        Args:
            oid: Object ID to remove.

        Returns:
            None.
        """
        self._store.pop(oid, None)
