import os, sqlite3, time
from pathlib import Path
from typing import Any
import sqlparse
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")
DB_PATH = Path(os.getenv("SQLITE_DB_PATH", str(HERE / "veterinary.db"))).expanduser()
MAX_ROWS = max(1, min(int(os.getenv("MAX_RESULT_ROWS", "500")), 5000))
TABLES = ["VMS26_Owners", "VMS26_Pets", "VMS26_Veterinarians", "VMS26_Appointments", "VMS26_Treatments", "VMS26_Payments"]

app = FastAPI(title="Veterinary Management SQL Studio", version="1.0")
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_ORIGIN","http://localhost:5173"),"http://127.0.0.1:5173"], allow_credentials=False, allow_methods=["GET","POST"], allow_headers=["Content-Type"])

class Query(BaseModel):
    query: str = Field(min_length=1, max_length=20000)

def db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB_PATH), timeout=10)
    c.execute("PRAGMA foreign_keys=ON")
    return c

def initialize():
    c = db()
    try:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS VMS26_Owners (
          owner_id INTEGER PRIMARY KEY, first_name TEXT NOT NULL, last_name TEXT NOT NULL,
          phone_number TEXT UNIQUE, email TEXT UNIQUE, address TEXT
        );
        CREATE TABLE IF NOT EXISTS VMS26_Pets (
          pet_id INTEGER PRIMARY KEY, pet_name TEXT NOT NULL, species TEXT NOT NULL,
          breed TEXT, sex TEXT CHECK(sex IN ('Male','Female','Unknown')),
          date_of_birth TEXT, owner_id INTEGER NOT NULL,
          FOREIGN KEY(owner_id) REFERENCES VMS26_Owners(owner_id)
        );
        CREATE TABLE IF NOT EXISTS VMS26_Veterinarians (
          vet_id INTEGER PRIMARY KEY, vet_name TEXT NOT NULL, specialization TEXT NOT NULL,
          phone_number TEXT UNIQUE, salary NUMERIC CHECK(salary >= 0)
        );
        CREATE TABLE IF NOT EXISTS VMS26_Appointments (
          appointment_id INTEGER PRIMARY KEY, pet_id INTEGER NOT NULL, vet_id INTEGER NOT NULL,
          appointment_date TEXT NOT NULL, reason TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'Scheduled' CHECK(status IN ('Scheduled','Completed','Cancelled')),
          FOREIGN KEY(pet_id) REFERENCES VMS26_Pets(pet_id),
          FOREIGN KEY(vet_id) REFERENCES VMS26_Veterinarians(vet_id)
        );
        CREATE TABLE IF NOT EXISTS VMS26_Treatments (
          treatment_id INTEGER PRIMARY KEY, appointment_id INTEGER NOT NULL,
          diagnosis TEXT NOT NULL, medication TEXT, treatment_cost NUMERIC NOT NULL CHECK(treatment_cost >= 0),
          notes TEXT,
          FOREIGN KEY(appointment_id) REFERENCES VMS26_Appointments(appointment_id)
        );
        CREATE TABLE IF NOT EXISTS VMS26_Payments (
          payment_id INTEGER PRIMARY KEY, owner_id INTEGER NOT NULL, amount NUMERIC NOT NULL CHECK(amount > 0),
          payment_date TEXT NOT NULL DEFAULT(date('now')), payment_method TEXT,
          payment_status TEXT NOT NULL CHECK(payment_status IN ('Paid','Pending','Failed')),
          FOREIGN KEY(owner_id) REFERENCES VMS26_Owners(owner_id)
        );
        """)
        if c.execute("SELECT COUNT(*) FROM VMS26_Owners").fetchone()[0] == 0:
            c.executemany("INSERT INTO VMS26_Owners VALUES(?,?,?,?,?,?)", [
                (1,"Aarav","Shah","9001000001","aarav.shah@example.com","12 Lake View Road"),
                (2,"Ananya","Rao","9001000002","ananya.rao@example.com","8 Green Park"),
                (3,"Rohan","Kumar","9001000003","rohan.kumar@example.com","21 Hill Street"),
                (4,"Diya","Nair","9001000004","diya.nair@example.com","5 Garden Avenue"),
                (5,"Karthik","Iyer","9001000005","karthik.iyer@example.com","17 River Road"),
                (6,"Meera","Patel","9001000006","meera.patel@example.com","44 Sunrise Lane")])
            c.executemany("INSERT INTO VMS26_Pets VALUES(?,?,?,?,?,?,?)", [
                (101,"Bruno","Dog","Labrador","Male","2021-04-12",1),
                (102,"Milo","Cat","Persian","Male","2022-08-20",2),
                (103,"Coco","Dog","Indie","Female","2020-11-05",3),
                (104,"Luna","Cat","Siamese","Female","2023-02-18",4),
                (105,"Oreo","Rabbit","Holland Lop","Male","2022-07-30",5),
                (106,"Bella","Dog","Beagle","Female","2021-09-14",6),
                (107,"Kiwi","Bird","Parakeet","Unknown","2023-12-22",1),
                (108,"Daisy","Dog","Golden Retriever","Female","2019-04-09",2)])
            c.executemany("INSERT INTO VMS26_Veterinarians VALUES(?,?,?,?,?)", [
                (11,"Dr. Neha Kapoor","General Practice","9012000001",65000),
                (12,"Dr. Arjun Menon","Surgery","9012000002",82000),
                (13,"Dr. Sara Thomas","Dermatology","9012000003",70000),
                (14,"Dr. Vikram Rao","Dentistry","9012000004",68000)])
            c.executemany("INSERT INTO VMS26_Appointments VALUES(?,?,?,?,?,?)", [
                (201,101,11,"2026-10-12 09:30","Annual check-up","Scheduled"),
                (202,102,13,"2026-10-12 10:30","Skin irritation","Scheduled"),
                (203,103,12,"2026-10-08 11:00","Limping","Completed"),
                (204,104,11,"2026-10-13 14:00","Vaccination","Scheduled"),
                (205,105,11,"2026-10-09 15:00","Digestive concern","Completed"),
                (206,106,13,"2026-10-14 09:00","Itching","Scheduled"),
                (207,107,11,"2026-10-15 12:00","Routine examination","Scheduled"),
                (208,108,12,"2026-10-07 16:00","Dental check","Completed")])
            c.executemany("INSERT INTO VMS26_Treatments VALUES(?,?,?,?,?,?)", [
                (301,203,"Minor leg strain","Rest and monitored activity",850,"Recheck if limp persists."),
                (302,205,"Mild gastrointestinal upset","Dietary management",600,"Hydration encouraged."),
                (303,208,"Dental tartar","Dental cleaning",1800,"Routine oral hygiene advised.")])
            c.executemany("INSERT INTO VMS26_Payments VALUES(?,?,?,?,?,?)", [
                (401,1,1200,"2026-10-08","UPI","Paid"),
                (402,2,900,"2026-10-09","Card","Paid"),
                (403,3,850,"2026-10-08","Cash","Pending"),
                (404,4,700,"2026-10-09","UPI","Paid"),
                (405,5,600,"2026-10-09","Card","Pending"),
                (406,6,1500,"2026-10-10","UPI","Paid")])
        c.commit()
    finally: c.close()

@app.on_event("startup")
def startup(): initialize()

@app.get("/api/health")
def health(): return {"ok":True,"database":"SQLite","service":"Veterinary Management SQL Studio"}

@app.get("/api/db-status")
def db_status():
    c=db()
    try: return {"connected":True,"database":"SQLite","sqliteVersion":c.execute("SELECT sqlite_version()").fetchone()[0],"tables":{t:c.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in TABLES}}
    finally: c.close()

@app.get("/api/schema")
def schema():
    c=db()
    try:
        result=[]
        for (name,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'VMS26_%' ORDER BY name").fetchall():
            cols=c.execute(f'PRAGMA table_info("{name}")').fetchall()
            result.append({"name":name,"columns":[{"name":r[1],"type":r[2] or "TEXT","length":None,"nullable":not bool(r[3])} for r in cols]})
        return {"tables":result}
    finally: c.close()

def parse_sql(raw):
    parts=[s.strip() for s in sqlparse.split(raw.strip()) if s.strip()]
    if not parts: raise HTTPException(400,"Enter a SQL statement.")
    if len(parts)!=1: raise HTTPException(400,"Run one SQL statement at a time.")
    statement=parts[0].removesuffix(";").strip()
    parsed=sqlparse.parse(statement)
    if not parsed: raise HTTPException(400,"Could not parse SQL.")
    token=next((t for t in parsed[0].flatten() if not t.is_whitespace and t.ttype not in sqlparse.tokens.Comment),None)
    first=token.value.upper() if token else ""
    kind="WITH" if first=="WITH" else parsed[0].get_type().upper()
    if kind=="UNKNOWN": kind=first
    if kind not in {"SELECT","WITH","INSERT","UPDATE","DELETE","CREATE","ALTER","DROP","REPLACE","PRAGMA"}: raise HTTPException(403,f"Statement type '{kind}' is not enabled.")
    return statement,kind

def val(v:Any):
    if isinstance(v,(str,int,float,bool)) or v is None: return v
    if isinstance(v,bytes): return v.hex()
    return str(v)

@app.post("/api/execute")
def execute(req:Query):
    statement,kind=parse_sql(req.query); c=db(); start=time.perf_counter()
    try:
        cur=c.cursor(); cur.execute(statement); ms=round((time.perf_counter()-start)*1000,2)
        if cur.description:
            columns=[x[0] for x in cur.description]; rows=cur.fetchmany(MAX_ROWS+1); truncated=len(rows)>MAX_ROWS; rows=rows[:MAX_ROWS]; c.rollback()
            return {"success":True,"statementType":kind,"columns":columns,"rows":[[val(v) for v in r] for r in rows],"rowCount":len(rows),"truncated":truncated,"message":f"{len(rows)} row(s) returned.","executionMs":ms}
        count=cur.rowcount if cur.rowcount>=0 else None; c.commit()
        msg=f"{count} row(s) affected. Changes committed." if kind in {"INSERT","UPDATE","DELETE","REPLACE"} else "Statement executed successfully."
        return {"success":True,"statementType":kind,"columns":[],"rows":[],"rowCount":count,"truncated":False,"message":msg,"executionMs":ms}
    except sqlite3.Error as e:
        c.rollback(); raise HTTPException(400,f"SQLite error: {str(e)[:1000]}")
    finally: c.close()
