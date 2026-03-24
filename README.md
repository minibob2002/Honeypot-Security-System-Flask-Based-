# Honeypot Security System (Flask-Based)
A lightweight yet powerful web-based honeypot application built with Flask that simulates a vulnerable environment to detect, log, and analyze cyber attack attempts in real time.  
This project acts like a digital “trapdoor castle” 🏰—inviting attackers in just enough to observe their behavior while keeping real systems safe.  

🚀 Features :
🔍 Real-Time Attack Detection Detects multiple attack types: SQL Injection Cross-Site Scripting (XSS) Path Traversal / LFI Command Injection Phishing attempts Malicious file uploads Brute-force patterns 
📊Comprehensive Logging Stores attack data (type, payload, username, timestamp, IP) Maintains structured logs in SQLite database 
🚨 Discord Alert Integration Instant alerts for detected attacks via webhook Rich embeds with attack details, IP, and user agent Daily summary reports with: Attack counts Breakdown by type Top attacking IPs 
🧠 AI-Powered Analysis Integrates with Google Gemini API Generates insights from logs: Attack trends Common patterns Suggested visualizations 
👤 User Simulation System Registration & login system to mimic real users Tracks suspicious behavior per session Auto logout after repeated suspicious actions 
📂 Secure File Upload Trap Accepts only .zip files Logs and flags suspicious uploads 🛠️ Admin Dashboard View logs (Hive view) Trigger Discord summaries Pause/resume notifications Test detection patterns 
🧪 Attack Simulation Endpoint Dedicated /hack route for testing payloads Built-in attack test suite for validation 

🧩 Tech Stack Backend: 
Flask (Python) Database: 
SQLite Notifications: 
Discord Webhooks AI Integration: 
Google Gemini API Frontend:
HTML templates (Jinja2) 

🎯 Use Cases Cybersecurity learning & demonstrations Penetration testing practice environments Intrusion detection system (IDS) prototyping Security research & attack pattern analysis 

⚠️ Disclaimer  This project is intended for educational and defensive security purposes only. Do not deploy it in production without proper hardening.  

🌟 Highlights  Think of it as a digital wildlife camera for hackers 📸—quietly observing, recording, and reporting every move without interfering… until it needs to.
