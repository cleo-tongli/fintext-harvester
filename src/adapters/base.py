from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any

class BaseAdapter(ABC):
    source_id: str = "base"

    @abstractmethod
    def iter_items(self) -> Iterable[Dict[str, Any]]:
        """yield dicts with: url, title, description, published_at, source_id/name"""
        ...
