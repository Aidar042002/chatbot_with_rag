from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class Document:
    id: Optional[str] = None
    text: str = ""
    content: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None
    source: Optional[str] = None