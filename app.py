from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import uvicorn

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String)

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    value = Column(Float)
    confidence = Column(Float)

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    preferences = Column(JSON)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app setup
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Seed data
@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    if not db.query(User).first():
        db.add(User(name="John Doe", email="john@example.com", role="admin"))
        db.commit()
    if not db.query(Forecast).first():
        db.add(Forecast(value=100.0, confidence=0.95))
        db.commit()
    db.close()

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/analytics", response_class=HTMLResponse)
async def read_analytics(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request})

@app.get("/users", response_class=HTMLResponse)
async def read_users(request: Request):
    return templates.TemplateResponse("users.html", {"request": request})

@app.get("/settings", response_class=HTMLResponse)
async def read_settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/api-docs", response_class=HTMLResponse)
async def read_api_docs(request: Request):
    return templates.TemplateResponse("api_docs.html", {"request": request})

# API Endpoints
@app.get("/api/forecast")
async def get_forecast(db: Session = Depends(get_db)):
    forecasts = db.query(Forecast).all()
    return forecasts

@app.post("/api/users")
async def create_user(name: str, email: str, role: str, db: Session = Depends(get_db)):
    user = User(name=name, email=email, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/api/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.put("/api/users/{id}")
async def update_user(id: int, name: str, email: str, role: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = name
    user.email = email
    user.role = role
    db.commit()
    db.refresh(user)
    return user

@app.delete("/api/users/{id}")
async def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
