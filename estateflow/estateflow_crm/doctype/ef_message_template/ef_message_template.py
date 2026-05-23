from frappe.model.document import Document

class EFMessageTemplate(Document):
    def render(self, variables: dict) -> str:
        body = self.body or ""
        for key, val in variables.items():
            body = body.replace("{{" + key + "}}", str(val))
        return body
