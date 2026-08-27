from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles 
from fastapi.responses import HTMLResponse
from pathlib import Path
from datetime import datetime
import shutil
import uuid

app = FastAPI(title="CivicAI")

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


app.mount("/uploads" ,
 StaticFiles(directory="uploads"),
 name="uploads")         

complaints = []


def analyze_complaint(text: str):
    text_lower = text.lower()

    if any(word in text_lower for word in [
        "pothole", "road", "street", "crack", "broken road"
    ]):
        return "Road Damage", "High", "Road Department", 85

    if any(word in text_lower for word in [
        "garbage", "waste", "trash", "dump", "dirty"
    ]):
        return "Garbage / Waste", "Medium", "Sanitation Department", 65

    if any(word in text_lower for word in [
        "water", "leak", "pipe", "drainage", "flood"
    ]):
        return "Water / Drainage Issue", "Critical", "Water Department", 95

    if any(word in text_lower for word in [
        "light", "streetlight", "lamp", "electricity"
    ]):
        return "Streetlight Issue", "Medium", "Electrical Department", 60

    if any(word in text_lower for word in [
        "traffic", "signal", "accident", "crossing"
    ]):
        return "Traffic Issue", "High", "Traffic Department", 80

    return "General Infrastructure Issue", "Medium", \
           "Municipal Department", 50


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CivicAI</title>

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #07111f;
                color: white;
            }

            .container {
                max-width: 1000px;
                margin: auto;
                padding: 30px 20px;
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
            }

            .header h1 {
                font-size: 48px;
                margin-bottom: 5px;
            }

            .header p {
                color: #aab8cc;
                font-size: 18px;
            }

            .card {
                background: #111f33;
                border: 1px solid #263a55;
                border-radius: 18px;
                padding: 30px;
                margin-bottom: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            }

            label {
                display: block;
                margin-top: 18px;
                margin-bottom: 8px;
                font-weight: bold;
            }

            textarea,
            input[type="text"],
            input[type="file"] {
                width: 100%;
                padding: 14px;
                border-radius: 10px;
                border: 1px solid #3b506d;
                background: #0b1728;
                color: white;
            }

            textarea {
                min-height: 130px;
                resize: vertical;
            }

            button {
                width: 100%;
                margin-top: 25px;
                padding: 15px;
                border: none;
                border-radius: 10px;
                background: #19c7a3;
                color: white;
                font-size: 17px;
                font-weight: bold;
                cursor: pointer;
            }

            button:hover {
                opacity: 0.9;
            }

            .stats {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
            }

            .stat {
                background: #172941;
                padding: 20px;
                border-radius: 12px;
                text-align: center;
            }

            .stat h2 {
                margin: 0;
                font-size: 30px;
            }

            .stat p {
                color: #aab8cc;
                margin-bottom: 0;
            }

            .dashboard-link {
                display: block;
                text-align: center;
                margin-top: 20px;
                color: #19c7a3;
                text-decoration: none;
                font-weight: bold;
            }

            @media (max-width: 700px) {
                .stats {
                    grid-template-columns: 1fr;
                }

                .header h1 {
                    font-size: 36px;
                }
            }
        </style>
    </head>

    <body>

        <div class="container">

            <div class="header">
                <h1>🏙️ CivicAI</h1>
                <p>
                    From Citizen Complaints to Predictive Governance
                </p>
            </div>

            <div class="card">

                <h2>Report a Civic Issue</h2>
                <p>
                    Submit a complaint and CivicAI will analyze,
                    prioritize and route it to the appropriate department.
                </p>

                <form action="/complaint"
                      method="post"
                      enctype="multipart/form-data">

                    <label>Complaint Description</label>

                    <textarea
                        name="text"
                        placeholder="Example: Large pothole near the college gate..."
                        required></textarea>

                    <label>Location</label>

                    <input
                        type="text"
                        name="location"
                        placeholder="Example: Near college gate"
                        required>

                    <label>Photo Evidence</label>

                    <input
                        type="file"
                        name="image"
                        accept="image/*">

                    <button type="submit">
                        🤖 Analyze Complaint with CivicAI
                    </button>

                </form>

                <a class="dashboard-link" href="/dashboard">
                    📊 View CivicAI Dashboard
                </a>

            </div>

        </div>

    </body>
    </html>
    """


@app.post("/complaint", response_class=HTMLResponse)
async def complaint(
    text: str = Form(...),
    location: str = Form(...),
    image: UploadFile | None = File(None)
):

    issue, severity, department, priority = analyze_complaint(text)

    complaint_id = "CIV-" + uuid.uuid4().hex[:6].upper()

    image_name = "No photo"

    if image and image.filename:
        safe_name = Path(image.filename).name
        image_path = UPLOAD_DIR / f"{complaint_id}_{safe_name}"

        with image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_name = safe_name

    complaint_data = {
        "id": complaint_id,
        "text": text,
        "location": location,
        "issue": issue,
        "severity": severity,
        "department": department,
        "priority": priority,
        "status": "Submitted",
        "image": image_name,
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }

    complaints.append(complaint_data)

    return f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>CivicAI Analysis</title>

        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #07111f;
                color: white;
            }}

            .container {{
                max-width: 850px;
                margin: auto;
                padding: 30px 20px;
            }}

            .card {{
                background: #111f33;
                border: 1px solid #263a55;
                border-radius: 18px;
                padding: 30px;
            }}

            .success {{
                color: #19c7a3;
                font-weight: bold;
            }}

            .result {{
                background: #172941;
                padding: 22px;
                border-radius: 14px;
                margin-top: 20px;
            }}

            .result p {{
                font-size: 17px;
            }}

            .id {{
                font-size: 25px;
                font-weight: bold;
                color: #19c7a3;
            }}

            .priority {{
                font-size: 28px;
                font-weight: bold;
            }}

            a {{
                color: #19c7a3;
                text-decoration: none;
            }}

            .button {{
                display: inline-block;
                margin-top: 20px;
                padding: 12px 20px;
                border-radius: 8px;
                background: #19c7a3;
                color: white;
            }}
        </style>
    </head>

    <body>

        <div class="container">

            <div class="card">

                <h1>🤖 CivicAI Analysis</h1>

                <p class="success">
                    ✓ Complaint successfully analyzed and routed
                </p>

                <div class="result">

                    <p>Complaint ID</p>
                    <div class="id">{complaint_id}</div>

                    <p><b>Issue:</b> {issue}</p>

                    <p><b>Severity:</b> {severity}</p>

                    <p>
                        <b>Priority Score:</b>
                        <span class="priority">{priority}/100</span>
                    </p>

                    <p><b>Department:</b> {department}</p>

                    <p><b>Location:</b> {location}</p>

                    <p><b>Photo:</b> {image_name}</p>

                    <p><b>Status:</b> Submitted</p>

                    <p><b>Submitted:</b>
                        {complaint_data["time"]}
                    </p>

                </div>

                <p>
                    CivicAI has identified the issue,
                    assigned its priority and routed it
                    to the responsible department.
                </p>

                <a class="button" href="/">
                    ← Submit Another Complaint
                </a>

                <a class="button" href="/dashboard">
                    📊 Dashboard
                </a>

            </div>

        </div>

    </body>
    </html>
    """


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():

    total = len(complaints)

    high_priority = sum(
        1 for c in complaints if c["priority"] >= 80
    )

    resolved = sum(
        1 for c in complaints if c["status"] == "Resolved"
    )

    rows = ""

    for c in reversed(complaints):

        if c["image"] != "No photo":
            image_html = (
                "<img src='/uploads/"
                + c["id"]
                + "_"
                + c["image"]
                + "' width='100'>"
            )
        else:
            image_html = "No photo"

        rows += f"""
        <tr>
            <td>{c["id"]}</td>
            <td>{c["issue"]}</td>
            <td>{c["severity"]}</td>
            <td>{c["priority"]}/100</td>
            <td>{c["department"]}</td>
            <td>{c["location"]}</td>
            <td>{image_html}</td>
            <td>{c["status"]}</td>
        </tr>
        """

    """
           
</td>
            </td>{c["status"]}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="8">
                No complaints submitted yet.
            </td>
                </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>CivicAI Dashboard</title>

        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #07111f;
                color: white;
            }}

            .container {{
                max-width: 1200px;
                margin: auto;
                padding: 30px 20px;
            }}

            h1 {{
                font-size: 40px;
            }}

            .stats {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin: 25px 0;
            }}

            .stat {{
                background: #111f33;
                border: 1px solid #263a55;
                border-radius: 15px;
                padding: 25px;
                text-align: center;
            }}

            .stat h2 {{
                font-size: 35px;
                margin: 0;
            }}

            .stat p {{
                color: #aab8cc;
            }}

            .table-card {{
                background: #111f33;
                border-radius: 15px;
                padding: 20px;
                overflow-x: auto;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 850px;
            }}

            th, td {{
                padding: 14px;
                border-bottom: 1px solid #263a55;
                text-align: left;
            }}

            th {{
                color: #19c7a3;
            }}

            a {{
                color: #19c7a3;
                text-decoration: none;
            }}
        </style>
    </head>

    <body>

        <div class="container">

            <h1>📊 CivicAI Dashboard</h1>

            <p>
                Real-time overview of citizen infrastructure complaints
            </p>

            <div class="stats">

                <div class="stat">
                    <h2>{total}</h2>
                    <p>Total Complaints</p>
                </div>

                <div class="stat">
                    <h2>{high_priority}</h2>
                    <p>High Priority</p>
                </div>

                <div class="stat">
                    <h2>{resolved}</h2>
                    <p>Resolved</p>
                </div>

            </div>

            <div class="table-card">

                <h2>Complaint Queue</h2>

                <table>

                    <tr>
                        <th>ID</th>
                        <th>Issue</th>
                        <th>Severity</th>
                        <th>Priority</th>
                        <th>Department</th>
                        <th>Location</th>
                        <th>Photo</th>
                        <th>Status</th>
                    </tr>

                    {rows}

                </table>

            </div>

            <br>

            <a href="/">← Report New Complaint</a>

        </div>

    </body>

    </html>
    """