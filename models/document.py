from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class Document:
    pg_id: Optional[int] = None
    qdrant_id: Optional[str] = None
    text: str = ""
    content: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None