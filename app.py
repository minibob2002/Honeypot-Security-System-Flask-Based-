from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3, os, re, datetime
import requests
import json
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = "supersecret"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

GEMINI_API_KEY = "your_gemini_api_key_here"  # Replace with your actual Gemini API key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY

# Discord Configuration
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', 'your_discord_webhook_url_here')  # Set this in your environment variables for security
DISCORD_ENABLED = bool(DISCORD_WEBHOOK_URL)
DISCORD_PAUSED = False  # Global flag to pause/resume notifications

# --- DB INIT ---
def init_db():
    with sqlite3.connect("honeypot.db") as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        email TEXT,
                        phone TEXT,
                        role TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS logs(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        attack_type TEXT,
                        details TEXT,
                        username TEXT,
                        timestamp TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS uploads(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        filename TEXT,
                        timestamp TEXT)""")
        conn.commit()
init_db()

# --- DISCORD NOTIFICATIONS ---
def send_discord_alert(attack_type: str, details: str, username: str, ip_address: str, user_agent: str = None):
    """Send real-time Discord notification for blocked attacks."""
    if not DISCORD_ENABLED or DISCORD_PAUSED:
        return
    
    try:
        # Create rich embed for Discord
        embed = {
            "title": "🚨 Honeypot Attack Detected",
            "color": 0xff0000,  # Red color
            "fields": [
                {
                    "name": "Attack Type",
                    "value": f"`{attack_type}`",
                    "inline": True
                },
                {
                    "name": "Username",
                    "value": f"`{username}`",
                    "inline": True
                },
                {
                    "name": "IP Address",
                    "value": f"`{ip_address}`",
                    "inline": True
                },
                {
                    "name": "Timestamp",
                    "value": f"<t:{int(datetime.datetime.now().timestamp())}:F>",
                    "inline": False
                },
                {
                    "name": "Attack Details",
                    "value": f"```{details[:1000]}```",  # Limit to 1000 chars
                    "inline": False
                }
            ],
            "footer": {
                "text": "Honeypot Security System"
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add user agent if available
        if user_agent:
            embed["fields"].append({
                "name": "User Agent",
                "value": f"`{user_agent[:200]}`",  # Limit user agent length
                "inline": False
            })
        
        # Prepare webhook payload
        payload = {
            "embeds": [embed],
            "username": "Honeypot Security",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2913/2913465.png"
        }
        
        # Send to Discord
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 204:
            print(f"✅ Discord alert sent for {attack_type} attack from {ip_address}")
        else:
            print(f"❌ Failed to send Discord alert: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Discord notification error: {e}")

def send_discord_summary():
    """Send daily summary of attacks to Discord."""
    if not DISCORD_ENABLED or DISCORD_PAUSED:
        return
    
    try:
        with sqlite3.connect("honeypot.db") as conn:
            # Get today's attack count
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM logs WHERE timestamp LIKE ?", (f"{today}%",))
            today_count = c.fetchone()[0]
            
            # Get attack type breakdown
            c.execute("SELECT attack_type, COUNT(*) FROM logs WHERE timestamp LIKE ? GROUP BY attack_type", (f"{today}%",))
            attack_breakdown = c.fetchall()
            
            # Get top attacking IPs
            c.execute("""
                SELECT SUBSTR(details, 6, INSTR(details, ']') - 6) as ip, COUNT(*) as count 
                FROM logs 
                WHERE timestamp LIKE ? AND details LIKE '[IP:%' 
                GROUP BY ip 
                ORDER BY count DESC 
                LIMIT 5
            """, (f"{today}%",))
            top_ips = c.fetchall()
        
        # Create summary embed
        embed = {
            "title": "📊 Daily Honeypot Summary",
            "color": 0x00ff00,  # Green color
            "fields": [
                {
                    "name": "Total Attacks Today",
                    "value": f"`{today_count}`",
                    "inline": True
                },
                {
                    "name": "Date",
                    "value": f"`{today}`",
                    "inline": True
                }
            ],
            "footer": {
                "text": "Honeypot Security System - Daily Report"
            },
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Add attack breakdown
        if attack_breakdown:
            breakdown_text = "\n".join([f"• {atk_type}: {count}" for atk_type, count in attack_breakdown])
            embed["fields"].append({
                "name": "Attack Types",
                "value": f"```{breakdown_text}```",
                "inline": False
            })
        
        # Add top IPs
        if top_ips:
            ips_text = "\n".join([f"• {ip}: {count} attacks" for ip, count in top_ips])
            embed["fields"].append({
                "name": "Top Attacking IPs",
                "value": f"```{ips_text}```",
                "inline": False
            })
        
        payload = {
            "embeds": [embed],
            "username": "Honeypot Security",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2913/2913465.png"
        }
        
        response = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 204:
            print(f"✅ Discord daily summary sent")
        else:
            print(f"❌ Failed to send Discord summary: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Discord summary error: {e}")

# --- LOGGING HELPERS ---
def log_event(attack_type: str, details: str, username: str = "Unknown"):
    """Write a single row into logs table and send Discord notification."""
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    details_with_ip = f"[IP: {ip}] {details}"
    
    # Log to database
    with sqlite3.connect("honeypot.db") as conn:
        conn.execute(
            "INSERT INTO logs (attack_type, details, username, timestamp) VALUES (?,?,?,?)",
            (attack_type, details_with_ip, username, str(datetime.datetime.now()))
        )
        conn.commit()
    
    # Send Discord notification for actual attacks (not benign activities)
    if attack_type not in ["Benign Search", "Benign/Unknown"]:
        send_discord_alert(attack_type, details, username, ip, user_agent)

# --- HONEYPOT DETECTION ---
# More comprehensive and less restrictive patterns
SQLI_RE   = r"(union|select|drop|insert|delete|update|where|--|#|;|'|\"|or\s+1\s*=\s*1|and\s+1\s*=\s*1|sleep\(|benchmark\(|load_file\(|into\s+outfile)"
XSS_RE    = r"(<script|</script>|<img|onerror|onload|<svg|javascript:|alert\(|document\.cookie|window\.location|eval\(|innerHTML)"
LFI_RE    = r"(\.\./|\.\.\\|/etc/passwd|boot\.ini|/etc/shadow|/proc/version|/etc/hosts|\.\.%2f|\.\.%5c)"
CMDI_RE   = r"(\|\||&&|;|cat\s|wget\s|curl\s|ping\s|nc\s|netcat|bash\s|sh\s|cmd\s|powershell|whoami|id\s|ls\s|dir\s)"
PHISH_RE  = r"(http[s]?://[^\s]+@|data:text/html|javascript:|vbscript:|onclick=|onmouseover=)"
BRUTE_FORCE_RE = r"(password|123456|qwerty|password123|admin123|root123|letmein|welcome|login|pass)"
FILE_UPLOAD_RE = r"(\.php|\.asp|\.jsp|\.exe|\.bat|\.sh|\.py|\.pl|\.phtml|\.jspx|\.aspx)"

def detect_attack(input_str: str, username: str = "Unknown"):
    """Detect common attacks; return list of matched types."""
    if not input_str:
        return []

    # Debug logging
    print(f"🔍 Checking input: '{input_str}' from user: {username}")
    
    attacks = []
    checks = [
        ("SQL Injection", SQLI_RE),
        ("XSS / Intrusion", XSS_RE),
        ("Path Traversal / LFI", LFI_RE),
        ("Command Injection", CMDI_RE),
        ("Phishing Attempt", PHISH_RE),
        ("Malicious File Upload", FILE_UPLOAD_RE),
    ]

    # Check for brute force only in password fields or suspicious contexts
    current_endpoint = request.endpoint if hasattr(request, 'endpoint') else 'Unknown'
    
    # Only flag as brute force if it's clearly a weak password, not a legitimate username
    if re.search(BRUTE_FORCE_RE, input_str, re.IGNORECASE):
        # Additional context check - don't flag legitimate usernames
        if not re.search(r"^(admin|root|administrator|test|guest|user)$", input_str, re.IGNORECASE):
            attacks.append("Brute Force Attempt")
            print(f"✅ Brute Force Attempt detected! Pattern: {BRUTE_FORCE_RE}")
        else:
            print(f"ℹ️ Legitimate username detected: '{input_str}' - not flagging as brute force")

    for label, pattern in checks:
        if re.search(pattern, input_str, re.IGNORECASE):
            attacks.append(label)
            print(f"✅ {label} detected! Pattern: {pattern}")

    if not attacks:
        print(f"❌ No attacks detected in: '{input_str}'")

    for atk in attacks:
        # Enhanced details with more context
        enhanced_details = f"Attack: {atk}\nPayload: {input_str}\nContext: {current_endpoint}"
        log_event(atk, enhanced_details, username)

    return attacks

# --- ROUTES ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        email = request.form["email"].strip()
        country_code = request.form["country_code"].strip()
        phone = request.form["phone"].strip()
        role = request.form["role"].strip()
        
        # Combine country code and phone number
        full_phone = f"{country_code} {phone}".strip()

        # Detect attacks
        detect_attack(username, username)
        detect_attack(password, username)
        detect_attack(email, username)
        detect_attack(phone, username)
        detect_attack(country_code, username)

        try:
            with sqlite3.connect("honeypot.db") as conn:
                conn.execute(
                    "INSERT INTO users (username,password,email,phone,role) VALUES (?,?,?,?,?)",
                    (username, password, email, full_phone, role)
                )
                conn.commit()
            flash("Registered successfully", "success")
            return redirect(url_for("login"))
        except Exception as e:
            log_event("Registration Error", str(e), username or "Unknown")
            flash("User already exists or invalid data!", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        detect_attack(username, username or "Unknown")
        detect_attack(password, username or "Unknown")

        with sqlite3.connect("honeypot.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            if user:
                session["user"] = username
                session["suspicious_count"] = 0  # Initialize counter
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials!", "danger")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    if "suspicious_count" not in session:
        session["suspicious_count"] = 0

    if request.method == "POST":
        info = request.form["info"]
        attacks = detect_attack(info, session["user"])
        if attacks:
            session["suspicious_count"] += 1
            flash(f"⚠ Suspicious activity detected: {attacks}. You are under observation!", "danger")
            if session["suspicious_count"] >= 3:
                flash("Too many suspicious actions! Logging out...", "danger")
                return redirect(url_for("logout"))

        file = request.files.get("file")
        if file and file.filename:
            if not file.filename.lower().endswith(".zip"):
                log_event("Invalid File Type", file.filename, session["user"])
                flash("Only .zip files are allowed!", "danger")
                session["suspicious_count"] += 1
                if session["suspicious_count"] >= 3:
                    flash("Too many suspicious actions! Logging out...", "danger")
                    return redirect(url_for("logout"))
            else:
                filename = f"{session['user']}_{file.filename}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                with sqlite3.connect("honeypot.db") as conn:
                    conn.execute(
                        "INSERT INTO uploads (username, filename, timestamp) VALUES (?,?,?)",
                        (session["user"], filename, str(datetime.datetime.now()))
                    )
                    conn.commit()
                flash("File uploaded successfully", "success")

    # List uploads
    with sqlite3.connect("honeypot.db") as conn:
        c = conn.cursor()
        c.execute("SELECT filename FROM uploads WHERE username=? ORDER BY id DESC", (session["user"],))
        uploads = [row[0] for row in c.fetchall()]

    return render_template("dashboard.html", user=session["user"], uploads=uploads)

@app.route("/search", methods=["POST"])
def search():
    if "user" not in session:
        return redirect(url_for("login"))

    query = request.form["query"]
    attacks = detect_attack(query, session["user"])
    if attacks:
        session["suspicious_count"] += 1
        flash(f"⚠ Attack detected in search: {attacks}. You are under observation!", "danger")
        if session["suspicious_count"] >= 3:
            flash("Too many suspicious actions! Logging out...", "danger")
            return redirect(url_for("logout"))
    else:
        log_event("Benign Search", query, session["user"])
        flash("No malicious activity detected.", "info")

    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("suspicious_count", None)
    session.pop("admin", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

# --- Other routes remain same ---
@app.route("/hive")
def hive():
    with sqlite3.connect("honeypot.db") as conn:
        logs = conn.execute(
            "SELECT id, attack_type, details, username, timestamp FROM logs ORDER BY id DESC"
        ).fetchall()
    return render_template("hive.html", logs=logs)

@app.route("/hack", methods=["GET","POST"])
def hack():
    if request.method == "POST":
        payload = request.form.get("payload", "")
        attacks = detect_attack(payload, "Anonymous Hacker")
        if attacks:
            flash(f"Attack trapped: {attacks}", "danger")
        else:
            log_event("Benign/Unknown", payload, "Anonymous Hacker")
            flash("No attack pattern matched; payload logged.", "info")
    return render_template("hack.html")

@app.route("/admin")
def admin():
    if not session.get("admin"):
        flash("Admin login required!", "danger")
        return redirect(url_for("admin_login"))
    return render_template("admin.html", discord_enabled=DISCORD_ENABLED, discord_paused=DISCORD_PAUSED)

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if username == "admin" and password == "admin":
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            log_event("Failed Admin Login", f"Attempted admin login with username: {username}", username)
            flash("Invalid admin credentials!", "danger")

    return render_template("admin_login.html")

@app.route("/analyze")
def analyze():
    # Fetch logs from DB
    with sqlite3.connect("honeypot.db") as conn:
        logs = conn.execute(
            "SELECT id, attack_type, details, username, timestamp FROM logs ORDER BY id DESC"
        ).fetchall()

    # Prepare data for Gemini
    log_texts = [f"ID: {log[0]}, Type: {log[1]}, User: {log[3]}, Details: {log[2]}, Time: {log[4]}" for log in logs]
    prompt = """
You are a cybersecurity analyst AI. Analyze the attack logs for trends, most common attack types, anomalies, and top targets. Summarize the key findings in 3-4 short, concise bullet points (no more than 4 lines). Suggest useful visualizations (e.g., bar chart of attack types, attack timeline, heatmap of IPs, top targeted users/resources).
Logs:
""" + "\n".join(log_texts)

    # Call Gemini API
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=30)
        gemini_result = response.json()
        analysis = gemini_result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No analysis returned.")
    except Exception as e:
        analysis = f"Error contacting Gemini API: {e}"

    # For visualization, prepare attack type counts
    from collections import Counter
    attack_types = [log[1] for log in logs]
    attack_counts = dict(Counter(attack_types))
    timestamps = [log[4] for log in logs]

    return render_template("analyze.html", analysis=analysis, attack_counts=attack_counts, timestamps=timestamps, logs=logs)

@app.route("/discord/summary")
def discord_summary():
    """Manually trigger Discord summary."""
    if not session.get("admin"):
        flash("Admin access required!", "danger")
        return redirect(url_for("admin_login"))
    
    try:
        send_discord_summary()
        flash("Discord summary sent successfully!", "success")
    except Exception as e:
        flash(f"Failed to send Discord summary: {e}", "danger")
    
    return redirect(url_for("admin"))

@app.route("/discord/test")
def discord_test():
    """Test Discord webhook with a sample alert."""
    if not session.get("admin"):
        flash("Admin access required!", "danger")
        return redirect(url_for("admin_login"))
    
    try:
        send_discord_alert(
            "Test Attack", 
            "This is a test notification to verify Discord integration is working properly.", 
            "admin", 
            "127.0.0.1", 
            "Test User Agent"
        )
        flash("Discord test notification sent!", "success")
    except Exception as e:
        flash(f"Failed to send Discord test: {e}", "danger")
    
    return redirect(url_for("admin"))

@app.route("/discord/pause")
def discord_pause():
    """Pause Discord notifications."""
    global DISCORD_PAUSED
    if not session.get("admin"):
        flash("Admin access required!", "danger")
        return redirect(url_for("admin_login"))
    
    DISCORD_PAUSED = True
    flash("🔇 Discord notifications paused!", "warning")
    return redirect(url_for("admin"))

@app.route("/discord/resume")
def discord_resume():
    """Resume Discord notifications."""
    global DISCORD_PAUSED
    if not session.get("admin"):
        flash("Admin access required!", "danger")
        return redirect(url_for("admin_login"))
    
    DISCORD_PAUSED = False
    flash("🔊 Discord notifications resumed!", "success")
    return redirect(url_for("admin"))

@app.route("/test/attacks")
def test_attacks():
    """Test attack detection patterns."""
    if not session.get("admin"):
        flash("Admin access required!", "danger")
        return redirect(url_for("admin_login"))
    
    test_payloads = [
        ("' OR 1=1 --", "SQL Injection"),
        ("<script>alert('xss')</script>", "XSS"),
        ("../../../etc/passwd", "Path Traversal"),
        ("cat /etc/passwd", "Command Injection"),
        ("admin", "Legitimate Username (should NOT trigger brute force)"),
        ("password", "Brute Force"),
        ("123456", "Brute Force"),
        ("test.php", "File Upload"),
        ("javascript:alert(1)", "XSS"),
        ("union select * from users", "SQL Injection"),
        ("<img src=x onerror=alert(1)>", "XSS"),
        ("normal text", "Should not match")
    ]
    
    results = []
    for payload, expected in test_payloads:
        attacks = detect_attack(payload, "test_user")
        detected = ", ".join(attacks) if attacks else "None"
        results.append({
            "payload": payload,
            "expected": expected,
            "detected": detected,
            "status": "✅" if attacks else "❌"
        })
    
    return f"""
    <h2>Attack Detection Test Results</h2>
    <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr>
            <th>Payload</th>
            <th>Expected</th>
            <th>Detected</th>
            <th>Status</th>
        </tr>
        {"".join([f'<tr><td>{r["payload"]}</td><td>{r["expected"]}</td><td>{r["detected"]}</td><td>{r["status"]}</td></tr>' for r in results])}
    </table>
    <br><a href="/admin">Back to Admin</a>
    """

if __name__ == "__main__":
    app.run(debug=True)
