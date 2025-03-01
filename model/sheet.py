from dataclasses import dataclass
from typing import Any, Dict


class GoogleSheetResponse:
    def __init__(self, id, data):
        self.id = id
        self.data = data

@dataclass
class GoogleSheetResponseDTO:
    id: str
    data: Dict[str, Any]

@dataclass
class DeleteResponseDTO:
    success: bool
    message: str