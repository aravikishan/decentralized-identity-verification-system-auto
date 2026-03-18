from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from uuid import uuid4
import sqlite3
from datetime import datetime

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE = 'identity_verification.db'

# Ensure tables are created
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    verification_status TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS verification_requests (
    request_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    submitted_data TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
''')
# Seed data
cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", (str(uuid4()), 'John Doe', 'john@example.com', 'verified'))
cursor.execute("INSERT OR IGNORE INTO verification_requests VALUES (?, ?, ?, ?, ?)", (str(uuid4()), '1', '{"id_number": "123456789"}', 'pending', datetime.now().isoformat()))
conn.commit()
conn.close()

# Models
class VerificationRequest(BaseModel):
    user_id: str
    submitted_data: dict

# Routes
@app.get('/', response_class=HTMLResponse)
async def read_home():
    return templates.TemplateResponse("home.html", {"request": {}})

@app.get('/verify', response_class=HTMLResponse)
async def read_verify():
    return templates.TemplateResponse("verify.html", {"request": {}})

@app.get('/dashboard', response_class=HTMLResponse)
async def read_dashboard():
    return templates.TemplateResponse("dashboard.html", {"request": {}})

@app.get('/api-docs', response_class=HTMLResponse)
async def read_api_docs():
    return templates.TemplateResponse("api_docs.html", {"request": {}})

@app.get('/about', response_class=HTMLResponse)
async def read_about():
    return templates.TemplateResponse("about.html", {"request": {}})

@app.post('/api/verify-identity')
async def verify_identity(request: VerificationRequest):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    request_id = str(uuid4())
    timestamp = datetime.now().isoformat()
    cursor.execute("INSERT INTO verification_requests VALUES (?, ?, ?, ?, ?)", (request_id, request.user_id, str(request.submitted_data), 'pending', timestamp))
    conn.commit()
    conn.close()
    return {"request_id": request_id, "status": "pending"}

@app.get('/api/verification-status/{user_id}')
async def get_verification_status(user_id: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT verification_status FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"user_id": user_id, "verification_status": result[0]}
    raise HTTPException(status_code=404, detail="User not found")

@app.get('/api/verification-history/{user_id}')
async def get_verification_history(user_id: str):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT request_id, submitted_data, status, timestamp FROM verification_requests WHERE user_id = ?", (user_id,))
    results = cursor.fetchall()
    conn.close()
    if results:
        history = [{"request_id": r[0], "submitted_data": r[1], "status": r[2], "timestamp": r[3]} for r in results]
        return {"user_id": user_id, "history": history}
    raise HTTPException(status_code=404, detail="No verification history found")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
