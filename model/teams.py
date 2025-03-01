from dataclasses import dataclass


@dataclass
class TeamsMessageRequestDTO:
    title: str
    text: str
    color: str = "#0078D7"

@dataclass
class TeamsMessageResponseDTO:
    success: bool
    message: str