import frappe

@frappe.whitelist()
def register_device_token(token, platform="Android"):
    """
    API for Mobile Apps to register FCM token.
    Method: POST
    Params: token, platform (device_id is no longer required)
    """
    if frappe.session.user == "Guest":
        frappe.throw("Authentication Required", frappe.PermissionError)

    user = frappe.session.user
    
    # Search for an existing token record for this USER
    # This implies a "Single Device per User" policy (the latest device overwrites the old one).
    existing_name = frappe.db.get_value("FCM Device Token", {"user": user}, "name")

    if existing_name:
        # Found a record for this user? Update the token.
        doc = frappe.get_doc("FCM Device Token", existing_name)
        doc.token = token
        doc.platform = platform
        doc.save(ignore_permissions=True)
    else:
        # No record found? Create a new one.
        # We auto-generate a device_id because the DocType field is likely Mandatory (reqd:1).
        new_doc = frappe.get_doc({
            "doctype": "FCM Device Token",
            "user": user,
            "token": token,
            "platform": platform
        })
        new_doc.insert(ignore_permissions=True)

    return {"status": "success", "message": "Token Registered"}