# 🛡️ Honeypot Security System

> A smart web honeypot that traps attackers, logs their moves, and sends real-time alerts with AI-powered analysis.

---

## 🚀 Overview

This project is a Flask-based web honeypot designed to simulate a vulnerable system and detect malicious activities in real time. It captures, logs, and analyzes attack patterns while notifying administrators instantly via Discord.

It serves as a practical tool for learning cybersecurity concepts, testing attack detection, and monitoring suspicious behavior.

---

## 🔥 Features

### 🔍 Attack Detection

* SQL Injection
* Cross-Site Scripting (XSS)
* Path Traversal / LFI
* Command Injection
* Phishing attempts
* Malicious file uploads
* Brute force patterns

### 📊 Logging & Monitoring

* Stores attack logs in SQLite database
* Captures IP address, payload, username, and timestamp
* Tracks user session behavior

### 🚨 Real-Time Alerts

* Discord webhook integration
* Rich alert messages with attack details
* Daily attack summaries

### 🧠 AI Analysis

* Integration with Google Gemini API
* Generates insights from attack logs
* Suggests visualization ideas

### 👤 User Simulation

* Registration & login system
* Suspicious activity tracking
* Auto logout after repeated threats

### 📂 File Upload Trap

* Accepts only `.zip` files
* Logs malicious upload attempts

### 🛠️ Admin Dashboard

* View logs (Hive view)
* Trigger Discord alerts manually
* Pause/resume notifications
* Test attack detection patterns

---

## 🧩 Tech Stack

* **Backend:** Flask (Python)
* **Database:** SQLite
* **Notifications:** Discord Webhooks
* **AI Integration:** Google Gemini API
* **Frontend:** HTML (Jinja2 templates)

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/honeypot-security-system.git
cd honeypot-security-system
```

### 2. Install dependencies

```bash
pip install flask requests
```

### 3. Set environment variables (optional)

```bash
export DISCORD_WEBHOOK_URL=your_webhook_url
```

### 4. Run the application

```bash
python app.py
```

### 5. Open in browser

```
http://127.0.0.1:5000
```

---

## 🔐 Default Admin Credentials

```
Username: admin
Password: admin
```

⚠️ Change these before deploying in any real environment.

---

## 🧪 Testing Attacks

You can test the honeypot using:

* `/hack` endpoint for manual payload testing
* `/test/attacks` for built-in detection validation

---

## 📊 Example Use Cases

* Cybersecurity learning & demos
* Penetration testing practice
* Intrusion detection system prototyping
* Attack pattern research

---

## ⚠️ Disclaimer

This project is intended for **educational and defensive purposes only**.
Do not use it for illegal activities or deploy it in production without proper security hardening.

---

## 🌟 Future Improvements

* Add dashboard visualizations (charts & graphs)
* Integrate more AI models
* Enhance detection with ML-based anomaly detection
* Dockerize the application

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and submit a pull request.

---

## 📜 License

This project is licensed under the MIT License.

---

## 💡 Author

Built for learning, experimentation, and catching attackers in the act.
