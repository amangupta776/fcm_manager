# Copyright (c) 2025, Aman Gupta and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from fcm_manager.api import send_notification

class FCMSettings(Document):
    def validate(self):
        """
        Run all validations before saving.
        """
        self.validate_filename()
        self.validate_file_privacy()
        self.validate_json_content()

    def validate_filename(self):
        """
        Ensure the uploaded file is actually a JSON file.
        """
        if not self.service_account_json:
            return

        # Check file extension
        if not self.service_account_json.lower().endswith(".json"):
            frappe.throw("<b>Invalid File Type:</b> The Service Account file must be a <b>.json</b> file.")

    def validate_file_privacy(self):
        if not self.service_account_json:
            return

        # 1. Fetch the File document associated with the URL
        file_entry = frappe.db.get_value(
            "File", 
            {"file_url": self.service_account_json}, 
            ["name", "is_private"], 
            as_dict=True
        )
        
        if not file_entry:
            return

        # 2. STRICTLY enforce privacy
        if not file_entry.is_private:
            frappe.throw(
                msg="<b>Security Risk:</b> The Service Account file is Public.<br>"
                    "Please delete this file, re-upload it, and <b>check the 'Private' box</b> in the upload dialog.",
                title="Security Validation Failed"
            )

    def validate_json_content(self):
        if not self.service_account_json:
            return

        try:
            # 3. Read the file content
            file_doc = frappe.get_doc("File", {"file_url": self.service_account_json})
            content = file_doc.get_content()
            
            data = json.loads(content)
            
            # 4. Check 'type' field (Google specific)
            if data.get("type") != "service_account":
                frappe.throw("<b>Invalid Content:</b> The JSON file does not appear to be a Google Service Account key (missing 'type': 'service_account').")

            # 5. Check for critical keys required by Google Auth
            required_keys = ["project_id", "private_key", "client_email"]
            missing = [key for key in required_keys if key not in data]
            
            if missing:
                frappe.throw(
                    f"The uploaded file is invalid. It is missing the following keys: {', '.join(missing)}"
                )

        except json.JSONDecodeError:
            frappe.throw("The uploaded file is not a valid JSON file.")
        except Exception:
            pass

@frappe.whitelist()
def test_fcm_notification(token, title, body):
    if not token:
        frappe.throw("Please enter a Test Device Token")
    
    send_notification(token, title, body)
    frappe.msgprint("Test Notification Queued!")