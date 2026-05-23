import frappe
from frappe.model.document import Document
from frappe.utils import cint


class EFProperty(Document):

    def get_share_url(self):
        return f"{frappe.utils.get_url()}/share/property/{self.name}"

    def get_formatted_price(self):
        lakh = 100000
        crore = 10000000
        if self.price >= crore:
            return f"₹{self.price / crore:.2f} Cr"
        elif self.price >= lakh:
            return f"₹{self.price / lakh:.0f}L"
        return f"₹{self.price:,.0f}"

    def get_amenities_list(self):
        if not self.amenities:
            return []
        return [a.strip() for a in self.amenities.split(",") if a.strip()]

    def get_whatsapp_message(self, lead_name):
        price = self.get_formatted_price()
        share_url = self.get_share_url()
        lines = [
            f"Hi {lead_name}, sharing details of *{self.title}* in {self.location}.",
            "",
            f"💰 Price: {price}",
            f"🏠 Type: {self.property_type}",
        ]
        if self.bedrooms:
            lines.append(f"🛏️ Bedrooms: {self.bedrooms} BHK")
        if self.size_sqft:
            lines.append(f"📐 Size: {self.size_sqft:.0f} sq ft")
        if self.furnishing_status:
            lines.append(f"🪑 Furnishing: {self.furnishing_status}")
        lines += ["", f"📸 Photos & Details: {share_url}", "", "Let me know if you'd like to schedule a visit! 😊"]
        return "\n".join(lines)
