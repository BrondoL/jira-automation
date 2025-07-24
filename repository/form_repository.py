import uuid
from util import save_response

class FormRepository():
    def save_response(self, req):
        power_app_id = uuid.uuid4()

        data = {
            "__PowerAppsId__": str(power_app_id),
            "Summary": req.get("summary"),
            "Description": req.get("description"),
            "Priority": req.get("priority"),
            "Assignee": req.get("assignee"),
            "Reporter": req.get("reporter")
        }
        save_response([data])

        return data