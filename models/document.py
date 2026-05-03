from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class Document:
    id: Optional[int] = None
    text: str = ""
    content: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None