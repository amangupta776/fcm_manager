---

# **FCM Manager**

### **FCM HTTP v1 support with Dynamic Whitelisting for Frappe/ERPNext**

Google deprecated the legacy FCM APIs in **June 2024**.
This app provides a seamless migration path by handling **OAuth 2.0 authentication via Service Accounts** and offering a **drop-in replacement** for push notification handling using the modern **Firebase HTTP v1 API**.

---
### Version
1.0.1

### Changelog / Updates
# v1.0.1
- fix: rename `api` folder to `whitelist_api` to prevent import conflicts

## 🚀 Features

* **🔐 HTTP v1 Support**
  Uses Google’s latest OAuth 2.0 protocol for secure authentication.

* **⚡ Zero-Code Notification**
  Automatically intercepts standard Frappe *System Notifications* (Mentions, Assignments, Workflow alerts) and sends them to user devices.

* **📝 Dynamic Whitelisting**
  Administrators can choose which DocTypes (e.g., *Sales Order*, *Task*) should trigger push notifications — preventing spam.

* **📱 Multi-Platform Support**
  Works with **Android**, **iOS**, and **Web**.

* **👤 User-Centric Device Mapping**
  Each device token is mapped to a User.
  If a user logs in on a new device, notifications automatically route there.

* **🧵 Background Jobs**
  Uses Frappe workers for async delivery so the UI remains fast.

---

## 📦 Installation

Run the following commands in your bench:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/amangupta776/fcm_manager.git
bench install-app fcm_manager
bench migrate
```

---

## 🔧 Configuration

### **1. Get Firebase Credentials**

1. Go to **Firebase Console**
2. Open **Project Settings → Service Accounts**
3. Click **Generate New Private Key**
4. Download the **JSON** file

---

### **2. Configure in Frappe**

1. Log into your Frappe/ERPNext Desk

2. Search for **FCM Settings**

3. Upload your Service Account JSON
   ⚠️ **Important:**
   When uploading, **check the “Private” checkbox**.
   Public files will be rejected for security reasons.

4. Enable FCM

5. (Optional) Configure Filters

   * Leave empty → *send all system notifications*
   * Add DocTypes → *send notifications only for these*

---

## 📲 Mobile App Integration

Your mobile application (Flutter / React Native / Native iOS / Native Android) must register the device token with Frappe after login.

### **Endpoint**

```
POST /api/method/fcm_manager.whitelist_api.v1.register_device_token.register_device_token
```

### **Payload**

```json
{
    "token": "fcm_device_token_string",
    "platform": "Android"
}
```

**Platform values:** `"Android"`, `"iOS"`, `"Web"`

**Authentication:**
Requires normal Frappe session (Cookies) or Token Auth.

---

## 🧪 Testing

1. Go to **FCM Settings**
2. Scroll to the **Test Console**
3. Enter a valid device token
4. Click **Send Test**

---

## 🤝 Contributing

This app uses **pre-commit** for formatting and linting.

Install and enable pre-commit:

```bash
cd apps/fcm_manager
pre-commit install
```

Tools used:

* **ruff**
* **eslint**
* **prettier**
* **pyupgrade**

---

## 🔄 CI

GitHub Actions workflows included:

* **CI**
  Installs the app and runs tests on every push to the `develop` branch.

* **Linters**
  Runs Frappe Semgrep rules and `pip-audit` on each Pull Request.

---

## 📄 License

**MIT**

---

If you'd like, I can also format this as a **Frappe Marketplace-ready README** or add **badges** (build, license, version).
