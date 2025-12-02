// Copyright (c) 2025, Aman Gupta and contributors
// For license information, please see license.txt

frappe.ui.form.on('FCM Settings', {
    send_test_notification: function (frm) {
        if (frm.is_dirty()) {
            frappe.msgprint(__("Please save settings before testing."));
            return;
        }
        frappe.call({
            method: "fcm_manager.fcm_manager.doctype.fcm_settings.fcm_settings.test_fcm_notification",
            args: {
                token: frm.doc.test_device_token,
                title: frm.doc.test_title,
                body: frm.doc.test_body
            },
            freeze: true,
            callback: function (r) {
                frappe.msgprint(r.message);
            }
        });
    }
});