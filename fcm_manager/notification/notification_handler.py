import frappe
from frappe.utils import strip_html
from fcm_manager.api import send_notification

def on_notification_log_insert(doc, method):
    """
    Triggered on 'after_insert' of 'Notification Log'.
    """
    # 1. Check if globally enabled
    settings = frappe.get_cached_doc("FCM Settings")
    if not settings.enabled:
        return

    # 2. Dynamic Whitelist Logic
    # If the child table 'allowed_doctypes' has rows, we filter.
    # If it is empty, we allow EVERYTHING.
    if settings.allowed_doctypes:
        allowed_list = [row.document_type for row in settings.allowed_doctypes]
        
        # If the notification source isn't in the list, abort.
        # doc.document_type is usually the source (e.g., 'Sales Order')
        if doc.document_type and doc.document_type not in allowed_list:
            return

    # 3. Validate Recipient
    user = doc.for_user
    if not user or user == "Guest":
        return

    # 4. Fetch User's Device Tokens
    tokens = frappe.get_all("FCM Device Token", filters={"user": user}, pluck="token")
    if not tokens:
        return

    # 5. Format Content
    title = doc.subject
    # Strip HTML tags (like <b>) and limit length
    body = strip_html(doc.email_content or "")[:200]

    # 6. Deep Linking Data
    data_payload = {
        "doctype": doc.document_type or "",
        "docname": doc.document_name or "",
        "click_action": "FLUTTER_NOTIFICATION_CLICK"
    }

    # 7. Send to all devices
    for token in tokens:
        send_notification(token, title, body, data=data_payload)