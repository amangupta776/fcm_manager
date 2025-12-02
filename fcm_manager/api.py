import frappe
import json
import requests
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Firebase Scope
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']

def send_notification(token, title, body, data=None):
    """
    Public function to queue notifications.
    """
    frappe.enqueue(
        'fcm_manager.api._send_internal',
        queue='short',
        token=token,
        title=title,
        body=body,
        data=data
    )
    # return _send_internal(token, title, body, data)

def _send_internal(token, title, body, data=None):
    """
    Internal worker function.
    """
    try:
        settings = frappe.get_cached_doc("FCM Settings")
        
        if not settings.enabled:
            frappe.log_error("FCM: Service is disabled in settings")
            return {"success": False, "error": "FCM disabled"}

        # 1. Get JSON Credential Path
        if not settings.service_account_json:
            frappe.log_error("FCM: Service Account JSON missing in settings")
            return {"success": False, "error": "Service account JSON not configured"}

        # Try to get the file path
        file_doc = frappe.get_doc("File", {"file_url": settings.service_account_json})
        
        # Get absolute path - handle both private and public files
        if hasattr(file_doc, 'get_full_path'):
            file_path = file_doc.get_full_path()
        else:
            # Fallback: construct path manually
            site_path = frappe.get_site_path()
            file_path = os.path.join(site_path, file_doc.file_url.lstrip('/'))

        if not os.path.exists(file_path):
            frappe.log_error(f"FCM: File not found at {file_path}")
            return {"success": False, "error": f"File not found: {file_path}"}

        # 2. Authenticate
        creds = service_account.Credentials.from_service_account_file(
            file_path, 
            scopes=SCOPES
        )
        creds.refresh(Request())
        access_token = creds.token
        project_id = creds.project_id

        if not project_id:
            frappe.log_error("FCM: Could not extract project_id from service account")
            return {"success": False, "error": "Invalid service account - no project_id"}

        # 3. Construct Endpoint & Headers
        endpoint = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
        }

        # 4. Construct Payload (v1 format)
        message_payload = {
            "message": {
                "token": token,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }

        # Custom Data (Must be strings in HTTP v1)
        if data:
            clean_data = {}
            for k, v in data.items():
                clean_data[k] = str(v) if v is not None else ""
            message_payload["message"]["data"] = clean_data

        # 5. Send Request
        response = requests.post(
            endpoint, 
            headers=headers, 
            json=message_payload,
            timeout=10
        )
        
        # Parse response
        response_data = response.json() if response.content else {}
        
        if response.status_code == 200:
            frappe.logger().info(f"FCM: Message sent successfully to {token[:20]}...")
            return {
                "success": True, 
                "response": response_data,
                "message_id": response_data.get("name")
            }
        else:
            error_msg = response_data.get("error", {}).get("message", response.text)
            frappe.log_error(
                f"FCM Send Error ({response.status_code}): {error_msg}\n"
                f"Token: {token[:20]}...\n"
                f"Response: {response.text}"
            )
            return {
                "success": False, 
                "error": error_msg,
                "status_code": response.status_code
            }
            
    except Exception as e:
        frappe.log_error(
            title="FCM Send Exception",
            message=f"Error: {str(e)}\nToken: {token[:20] if token else 'None'}..."
        )
        return {"success": False, "error": str(e)}