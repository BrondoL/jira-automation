from repository.form_repository import FormRepository


class FormService:
    def __init__(self, repository: FormRepository):
        self.repository = repository

    def save_response(self, req):
        form = self.repository.save_response(req)

        return form