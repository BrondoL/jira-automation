from typing import List

from model import sheet
from util import save_response

class GetAllGoogleSheetResponsesService:
    def __init__(self, repository):
        self.repository = repository

    def execute(self) -> List[sheet.GoogleSheetResponseDTO]:
        responses = self.repository.get_all_responses()

        response_data = []
        for response in responses:
            response_data.append(response.data)
        save_response(response_data)

        return [sheet.GoogleSheetResponseDTO(id=resp.id, data=resp.data) for resp in responses]

class DeleteAllGoogleSheetResponsesService:
    def __init__(self, repository):
        self.repository = repository

    def execute(self) -> sheet.DeleteResponseDTO:
        success = self.repository.delete_all_responses()
        message = "All responses deleted successfully" if success else "Failed to delete responses"
        return sheet.DeleteResponseDTO(success=success, message=message)