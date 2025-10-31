from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import File, UploadFile
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pandas as pd
import io
import os
from pathlib import Path
from ml.pipeline import ModelManager
from models import Base, get_db, User, Prediction, Message, StudentMetrics, init_db
from sqlalchemy.orm import Session
from auth import get_password_hash, verify_password, create_access_token, get_current_user, require_admin
from starlette.responses import StreamingResponse

app = FastAPI(title="Student Performance Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB and model manager
init_db()
model_manager = ModelManager()

# API router under /api
api = APIRouter(prefix="/api")

class PredictRequest(BaseModel):
    study_hours: float
    attendance: float
    previous_marks: float
    participation: float
    internet_access: int
    parental_education: int

class PredictResponse(BaseModel):
    prediction: int
    label: str
    probabilities: Optional[Dict[str, float]] = None

class TrainResponse(BaseModel):
    best_model: str
    metrics: Dict[str, float]

class StudentHomeResponse(BaseModel):
    upcoming_exams: List[Dict[str, str]]
    pass_probabilities: Dict[str, float]
    suggestions: List[str]

class MessageIn(BaseModel):
    to_user_id: int
    text: str

class EstimateIn(BaseModel):
    planned_hours: float
    user_id: Optional[int] = None

class AdminExportResponse(BaseModel):
    students: List[Dict[str, Any]]

@api.post("/auth/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    # Bootstrap: if there is no administrator yet, first registered user becomes admin
    is_first_admin = db.query(User).filter(User.role == "administrator").first() is None
    role = "administrator" if is_first_admin else "student"
    user = User(username=username, password_hash=get_password_hash(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@api.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "uid": user.id, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "username": user.username, "role": user.role}

@api.post("/setup/promote")
def setup_promote(username: str, key: str, db: Session = Depends(get_db)):
    expected = os.environ.get("ADMIN_SETUP_KEY", "")
    if not expected or key != expected:
        raise HTTPException(status_code=403, detail="Invalid setup key")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = "administrator"
    db.commit()
    return {"ok": True, "username": user.username, "role": user.role}

@api.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    df = pd.DataFrame([payload.dict()])
    pred, prob = model_manager.predict(df)
    label = "Pass" if int(pred[0]) == 1 else "Fail"

    # Log prediction
    proba_1 = None
    try:
        if isinstance(prob, list) and len(prob) > 0 and "1" in prob[0]:
            proba_1 = float(prob[0]["1"])
    except Exception:
        proba_1 = None
    p = Prediction(user_id=current_user.id, features=df.to_json(), prediction=int(pred[0]), proba_1=proba_1)
    db.add(p)
    db.commit()

    probs_fmt = {str(k): float(v) for k, v in (prob[0].items() if isinstance(prob, list) else prob.items())} if prob is not None else None
    return {"prediction": int(pred[0]), "label": label, "probabilities": probs_fmt}

@api.post("/train", response_model=TrainResponse)
def train(current_user: User = Depends(get_current_user)):
    best_name, metrics = model_manager.train_and_save()
    return {"best_model": best_name, "metrics": metrics}

@api.get("/metrics")
def metrics():
    return model_manager.metrics or {"detail": "Model not trained yet"}

@api.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "role": current_user.role}

@api.get("/student/summary")
def student_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Prefer latest StudentMetrics if available
    m = db.query(StudentMetrics).filter(StudentMetrics.user_id == current_user.id).order_by(StudentMetrics.created_at.desc()).first()
    if m and m.pass_probability is not None:
        return {"count": 1, "pass_probability": float(m.pass_probability)}
    # Otherwise, aggregate user's recent predictions to compute average pass probability
    rows = db.query(Prediction).filter(Prediction.user_id == current_user.id).order_by(Prediction.created_at.desc()).limit(200).all()
    if not rows:
        return {"count": 0, "pass_probability": None}
    probas = [r.proba_1 for r in rows if r.proba_1 is not None]
    if probas:
        avg = float(sum(probas) / len(probas))
    else:
        passes = sum(1 for r in rows if r.prediction == 1)
        avg = passes / len(rows)
    return {"count": len(rows), "pass_probability": avg}

@api.get("/student/metrics")
def student_metrics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    m = (
        db.query(StudentMetrics)
        .filter(StudentMetrics.user_id == current_user.id)
        .order_by(StudentMetrics.created_at.desc())
        .first()
    )
    if not m:
        return {
            "test1": None,
            "test2": None,
            "test3": None,
            "avg_percent": None,
            "attendance": None,
            "predicted_next_exam": None,
            "pass_probability": None,
            "created_at": None,
        }
    return {
        "test1": m.test1,
        "test2": m.test2,
        "test3": m.test3,
        "avg_percent": m.avg_percent,
        "attendance": m.attendance,
        "predicted_next_exam": m.predicted_next_exam,
        "pass_probability": m.pass_probability,
        "created_at": m.created_at.isoformat(),
    }

@api.get("/admin/export", response_model=AdminExportResponse)
def admin_export(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    users = db.query(User).filter(User.role == "student").all()
    items = []
    for u in users:
        rows = db.query(Prediction).filter(Prediction.user_id == u.id).order_by(Prediction.created_at.desc()).limit(200).all()
        probas = [r.proba_1 for r in rows if r.proba_1 is not None]
        if probas:
            avg = float(sum(probas) / len(probas))
        else:
            # fallback: use ratio of predicted passes
            passes = sum(1 for r in rows if r.prediction == 1)
            avg = passes / len(rows)
        items.append({"user": {"id": u.id, "username": u.username}, "count": len(rows), "pass_probability": avg})
    return {"students": items}

@api.post("/admin/upload")
def admin_upload(file: UploadFile = File(...), db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    # Accept CSV with columns: username, prediction, proba_1(optional), created_at(optional ISO)
    import csv, io as _io, datetime as _dt
    raw = file.file.read()
    text = raw.decode("utf-8", errors="ignore")
    reader = csv.DictReader(_io.StringIO(text))
    created = 0
    for row in reader:
        username = (row.get("username") or row.get("user") or "").strip()
        if not username:
            continue
        u = db.query(User).filter(User.username == username).first()
        if not u:
            continue
        try:
            pred = int(row.get("prediction", "")) if row.get("prediction") not in (None, "") else None
        except Exception:
            pred = None
        try:
            p1 = row.get("proba_1")
            proba_1 = float(p1) if p1 not in (None, "") else None
        except Exception:
            proba_1 = None
        ts = row.get("created_at")
        try:
            created_at = _dt.datetime.fromisoformat(ts) if ts else _dt.datetime.utcnow()
        except Exception:
            created_at = _dt.datetime.utcnow()
        p = Prediction(user_id=u.id, features="{}", prediction=pred if pred is not None else 0, proba_1=proba_1, created_at=created_at)
        db.add(p)
        created += 1
    db.commit()
    return {"inserted": created}

@api.get("/admin/metrics")
def admin_metrics(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    rows = db.query(StudentMetrics, User).join(User, StudentMetrics.user_id == User.id).order_by(StudentMetrics.created_at.desc()).all()
    out = []
    for m, u in rows:
        out.append({
            "id": m.id,
            "user_id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "test1": m.test1,
            "test2": m.test2,
            "test3": m.test3,
            "avg_percent": m.avg_percent,
            "attendance": m.attendance,
            "pass_probability": m.pass_probability,
            "predicted_next_exam": m.predicted_next_exam,
            "suggestion": m.suggestion,
            "created_at": m.created_at.isoformat(),
        })
    return {"items": out, "count": len(out)}

@api.get("/admin/student/{user_id}/metrics")
def admin_student_latest_metrics(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    m = (
        db.query(StudentMetrics)
        .filter(StudentMetrics.user_id == user_id)
        .order_by(StudentMetrics.created_at.desc())
        .first()
    )
    if not m:
        return {
            "test1": None,
            "test2": None,
            "test3": None,
            "predicted_next_exam": None,
            "pass_probability": None,
            "suggestion": None,
            "created_at": None,
        }
    return {
        "test1": m.test1,
        "test2": m.test2,
        "test3": m.test3,
        "predicted_next_exam": m.predicted_next_exam,
        "pass_probability": m.pass_probability,
        "suggestion": m.suggestion,
        "created_at": m.created_at.isoformat(),
    }

class SuggestionIn(BaseModel):
    suggestion: str

@api.post("/admin/student/{user_id}/suggestion")
def admin_update_suggestion(user_id: int, body: SuggestionIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    m = (
        db.query(StudentMetrics)
        .filter(StudentMetrics.user_id == user_id)
        .order_by(StudentMetrics.created_at.desc())
        .first()
    )
    if not m:
        m = StudentMetrics(user_id=user_id, suggestion=body.suggestion)
        db.add(m)
    else:
        m.suggestion = body.suggestion
    db.commit()
    return {"ok": True}

@api.post("/admin/metrics/{metrics_id}/suggestion")
def admin_update_row_suggestion(metrics_id: int, body: SuggestionIn, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    m = db.query(StudentMetrics).filter(StudentMetrics.id == metrics_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Metrics row not found")
    m.suggestion = body.suggestion
    db.commit()
    return {"ok": True, "id": metrics_id}

@api.post("/admin/metrics/import")
def admin_metrics_import(file: UploadFile = File(...), db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    # CSV columns (case-insensitive, flexible): Username, Test 1, Test 2, Test 3, Teacher Suggestions, Pass Probability, Predicted Next Exam
    # Robust parsing: auto-detect delimiter (comma/semicolon/tab), strip % symbols, accept integer percentages
    import csv, io as _io
    raw = file.file.read()
    text = raw.decode("utf-8", errors="ignore")
    sample = text[:1024]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        delim = dialect.delimiter
    except Exception:
        # fallback: detect tab if line contains tabs, else comma
        delim = "\t" if "\t" in sample else ","
    reader = csv.DictReader(_io.StringIO(text), delimiter=delim)
    # First pass: parse all rows to build a small training set from this upload
    parsed_rows = []
    skipped_users = []
    total_rows = 0
    for row in reader:
        total_rows += 1
        def pick(*keys):
            # direct hit
            for k in keys:
                if k in row and row[k] != "":
                    return row[k]
            # case-insensitive + trimmed headers
            lower = { (k or "").strip().lower(): v for k, v in row.items() }
            for k in keys:
                kk = (k or "").strip().lower()
                if kk in lower and lower[kk] != "":
                    return lower[kk]
            # normalized (remove spaces/underscores)
            norm = { ((k or "").strip().lower().replace(" ","").replace("_","")): v for k, v in row.items() }
            for k in keys:
                nk = (k or "").strip().lower().replace(" ","").replace("_","")
                if nk in norm and norm[nk] != "":
                    return norm[nk]
            return None
        username = (pick("Username", "User", "Name") or "").strip()
        if not username:
            skipped_users.append({"username": "(empty)", "reason": "Empty username"})
            continue
        u = db.query(User).filter(User.username == username).first()
        if not u:
            # Try by full_name
            u = db.query(User).filter(User.full_name == username).first()
        if not u:
            skipped_users.append({"username": username, "reason": "User not found in database"})
            continue
        def to_float(v):
            try:
                if v is None:
                    return None
                s = str(v).strip().replace('%','')
                if s == '':
                    return None
                return float(s)
            except Exception:
                return None
        t1 = to_float(pick("Test 1", "Test1"))
        t2 = to_float(pick("Test 2", "Test2"))
        t3 = to_float(pick("Test 3", "Test3"))
        # Optional: Avg % and Attendance
        avgp = to_float(pick("Avg %", "Avg%", "Average %", "Average", "Avg"))
        if avgp is not None and avgp > 1.0:
            avgp = avgp/100.0
        attend = to_float(pick("Attendance", "Attendance %", "Attendance%"))
        if attend is not None and attend > 1.0:
            attend = attend/100.0
        # Accept multiple header variants for pass probability
        pp = to_float(pick(
            "Pass Probability","PassProbability","Pass Prob","PassProb","Pass_%","Pass%","PassProbability%"
        ))
        if pp is not None and pp > 1.0:
            pp = pp/100.0
        # Accept multiple header variants for predicted marks
        pne = to_float(pick(
            "Predicted Next Exam","PredictedNextExam","Predicted","Estimated Marks","EstimatedMarks","Estimated Marks (next exam)"
        ))
        sugg = pick("Teacher Suggestions", "Suggestion", "Tips")
        # Derive avg_percent if not provided
        if avgp is None:
            nums = [v for v in [t1, t2, t3] if v is not None]
            avgp = (sum(nums)/len(nums))/100.0 if nums else None
        parsed_rows.append({
            "user": u,
            "username": username,
            "t1": t1, "t2": t2, "t3": t3,
            "avgp": avgp, "attend": attend,
            "pp": pp, "pne": pne, "sugg": sugg
        })

    # Train simple models on this upload if enough data
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    except Exception:
        LogisticRegression = None  # type: ignore
        RandomForestClassifier = None  # type: ignore
        RandomForestRegressor = None  # type: ignore
    import numpy as _np

    # Build training frames only with complete features
    train_rows = [r for r in parsed_rows if (r["t1"] is not None and r["t2"] is not None and r["t3"] is not None and r["attend"] is not None)]
    inserted = 0
    clf_lr = None
    clf_rf = None
    reg_rf = None
    if len(train_rows) >= 5 and RandomForestRegressor is not None:
        X = _np.array([[tr["t1"], tr["t2"], tr["t3"], tr["attend"]*100.0] for tr in train_rows], dtype=float)
        # classification label from rule
        y_cls = _np.array([1 if ((tr["avgp"] or 0) >= 0.6 and (tr["attend"] or 0) >= 0.8) else 0 for tr in train_rows], dtype=int)
        # regression target marks from avg percent as proxy (0-100)
        y_reg = _np.array([((tr["avgp"] or 0)*100.0) for tr in train_rows], dtype=float)
        try:
            if LogisticRegression is not None:
                clf_lr = LogisticRegression(max_iter=1000)
                clf_lr.fit(X, y_cls)
        except Exception:
            clf_lr = None
        try:
            if RandomForestClassifier is not None:
                clf_rf = RandomForestClassifier(n_estimators=200, random_state=42)
                clf_rf.fit(X, y_cls)
        except Exception:
            clf_rf = None
        try:
            if RandomForestRegressor is not None:
                reg_rf = RandomForestRegressor(n_estimators=200, random_state=42)
                reg_rf.fit(X, y_reg)
        except Exception:
            reg_rf = None

    # Second pass: insert rows with predicted pp/pne if missing
    for r in parsed_rows:
        u = r["user"]
        t1, t2, t3 = r["t1"], r["t2"], r["t3"]
        avgp, attend = r["avgp"], r["attend"]
        pp, pne, sugg = r["pp"], r["pne"], r["sugg"]
        # Predict if missing
        if (pp is None or pne is None) and (t1 is not None and t2 is not None and t3 is not None and attend is not None):
            feat = _np.array([[t1, t2, t3, attend*100.0]], dtype=float)
            # predicted marks
            est_marks = None
            if reg_rf is not None:
                try:
                    est_marks = float(reg_rf.predict(feat)[0])
                except Exception:
                    est_marks = None
            # pass probability by averaging available classifiers
            probs = []
            for clf in (clf_lr, clf_rf):
                if clf is not None:
                    try:
                        proba = clf.predict_proba(feat)[0][1]
                        probs.append(float(proba))
                    except Exception:
                        pass
            est_prob = float(sum(probs)/len(probs)) if probs else None
            if pne is None and est_marks is not None:
                pne = est_marks
            if pp is None and est_prob is not None:
                pp = est_prob
        # Final fallback heuristic if still missing
        if pne is None or pp is None:
            a = avgp if avgp is not None else 0.0
            at = attend if attend is not None else 0.0
            est = max(0.0, min(1.0, 0.7*a + 0.3*at)) * 100.0
            if pne is None:
                pne = est
            if pp is None:
                pp = est/100.0
        m = StudentMetrics(user_id=u.id, test1=t1, test2=t2, test3=t3, avg_percent=avgp, attendance=attend, pass_probability=pp, predicted_next_exam=pne, suggestion=sugg)
        db.add(m)
        try:
            import json as _json
            feats = {"test1": t1, "test2": t2, "test3": t3, "attendance": attend, "avg_percent": avgp, "predicted_next_exam": pne}
            pred_label = 1 if (pne is not None and pne >= 50) else (1 if (pp is not None and pp >= 0.5) else 0)
            p = Prediction(user_id=u.id, features=_json.dumps(feats), prediction=pred_label, proba_1=pp)
            db.add(p)
        except Exception:
            pass
        inserted += 1
    db.commit()
    return {
        "inserted": inserted,
        "total_rows": total_rows,
        "skipped": len(skipped_users),
        "skipped_details": skipped_users[:10]  # Show first 10 skipped users
    }

@api.delete("/admin/metrics/{metrics_id}")
def admin_metrics_delete(metrics_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    m = db.query(StudentMetrics).filter(StudentMetrics.id == metrics_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Metrics row not found")
    db.delete(m)
    db.commit()
    return {"deleted": 1, "id": metrics_id}

@api.delete("/admin/metrics/clear_all")
def admin_metrics_clear(username: str = "", db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    q = db.query(StudentMetrics)
    if username:
        u = db.query(User).filter(User.username == username).first()
        if not u:
            return {"deleted": 0}
        q = q.filter(StudentMetrics.user_id == u.id)
    count = q.count()
    q.delete(synchronize_session=False)
    db.commit()
    return {"deleted": count}

# Allow POST as a fallback for environments disallowing DELETE from browser
@api.post("/admin/metrics/clear_all")
def admin_metrics_clear_post(username: str = "", db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return admin_metrics_clear(username=username, db=db, admin=admin)

@api.get("/admin/search")
def admin_search(q: str = "", db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    query = db.query(User).filter(User.role == "student")
    if q:
        query = query.filter(User.username.ilike(f"%{q}%"))
    results = query.order_by(User.username.asc()).limit(50).all()
    return [{"id": u.id, "username": u.username, "role": u.role} for u in results]

@api.get("/assigned_admin")
def assigned_admin(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Return first administrator as assigned admin for simplicity
    admin_user = db.query(User).filter(User.role == "administrator").order_by(User.id.asc()).first()
    if not admin_user:
        raise HTTPException(status_code=404, detail="No administrator configured")
    return {"id": admin_user.id, "username": admin_user.username}

@api.get("/admin/student/{user_id}/summary")
def admin_student_summary(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    rows = db.query(Prediction).filter(Prediction.user_id == user_id).order_by(Prediction.created_at.desc()).limit(200).all()
    probas = [r.proba_1 for r in rows if r.proba_1 is not None]
    if probas:
        prob = float(sum(probas)/len(probas))
    else:
        prob = (sum(1 for r in rows if r.prediction==1)/len(rows)) if rows else None
    return {"user": {"id": u.id, "username": u.username, "role": u.role}, "count": len(rows), "pass_probability": prob}

@api.get("/messages")
def list_messages(with_user: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Only allow messages where current user is participant
    msgs = (
        db.query(Message)
        .filter(
            ((Message.from_user_id == current_user.id) & (Message.to_user_id == with_user)) |
            ((Message.from_user_id == with_user) & (Message.to_user_id == current_user.id))
        )
        .order_by(Message.created_at.asc())
        .all()
    )
    return [
        {"id": m.id, "from_user_id": m.from_user_id, "to_user_id": m.to_user_id, "text": m.text, "created_at": m.created_at.isoformat()}
        for m in msgs
    ]

@api.post("/messages")
def send_message(payload: MessageIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Admins can message any student; students can only send to admins who messaged them or to admin generally
    # For simplicity, allow sending to any existing user
    target = db.query(User).filter(User.id == payload.to_user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Recipient not found")
    m = Message(from_user_id=current_user.id, to_user_id=payload.to_user_id, text=payload.text)
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"id": m.id, "created_at": m.created_at.isoformat()}

@api.post("/estimate")
def estimate_probability(body: EstimateIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Determine target user: admin may pass user_id; students default to themselves
    target_user_id = body.user_id if (body.user_id and current_user.role == "administrator") else current_user.id
    # Find last features for target user
    last = db.query(Prediction).filter(Prediction.user_id == target_user_id).order_by(Prediction.created_at.desc()).first()
    # If no history, estimate with simple mapping of planned hours -> probability baseline
    if not last:
        z = max(0.0, min(1.0, (body.planned_hours or 0)/6.0))
        prob = 1/(1+pow(2.71828, -(8*z-4)))
        return {"probability": float(prob)}
    import json as _json
    try:
        feats = _json.loads(last.features)
        if isinstance(feats, dict):
            x = list(feats.values())[0] if feats else {}
        else:
            x = {}
    except Exception:
        x = {}
    x = dict(x)
    x["study_hours"] = float(body.planned_hours or 0)
    df = pd.DataFrame([x])
    _, prob = model_manager.predict(df)
    p1 = None
    if isinstance(prob, list) and len(prob)>0:
        p1 = prob[0].get("1")
    if p1 is None and isinstance(prob, dict):
        p1 = prob.get("1")
    if p1 is None:
        p1 = 0.5
    return {"probability": float(p1)}

@api.get("/student/home", response_model=StudentHomeResponse)
def student_home(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ("student", "administrator"):
        raise HTTPException(status_code=403, detail="Unknown role")
    # Basic upcoming exam schedule (could be sourced from DB later)
    upcoming = [
        {"name": "Mid-term", "date": "2025-11-15"},
        {"name": "Internal", "date": "2025-12-05"},
        {"name": "End-semester", "date": "2026-01-10"},
    ]
    rows = db.query(Prediction).filter(Prediction.user_id == current_user.id).order_by(Prediction.created_at.desc()).limit(100).all()
    # Probability per exam derived from historical average as a simple baseline
    probas = [r.proba_1 for r in rows if r.proba_1 is not None]
    if probas:
        base = float(sum(probas) / len(probas))
    else:
        passes = sum(1 for r in rows if r.prediction == 1)
        base = passes / len(rows) if rows else 0.5
    pass_probs = {e["name"]: base for e in upcoming}
    # Simple suggestions from latest features if available
    tips: List[str] = []
    if rows:
        import json as _json
        try:
            feats = _json.loads(rows[0].features)
            if isinstance(feats, dict):
                v = list(feats.values())[0] if feats else {}
            else:
                v = {}
        except Exception:
            v = {}
        study = float(v.get("study_hours", 0) or 0)
        attend = float(v.get("attendance", 0) or 0)
        prev = float(v.get("previous_marks", 0) or 0)
        part = float(v.get("participation", 0) or 0)
        if study < 2: tips.append("Increase daily study time to at least 2 hours.")
        if attend < 80: tips.append("Improve attendance to above 80% for better outcomes.")
        if prev < 60: tips.append("Revise weak topics from past exams; target previous marks > 60%.")
        if part < 5: tips.append("Participate more in class/worksheets to boost understanding.")
    if not tips:
        tips = ["Keep up the good work! Maintain consistency and practice past papers."]
    return {"upcoming_exams": upcoming, "pass_probabilities": pass_probs, "suggestions": tips}

@api.post("/bulk_predict")
def bulk_predict(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    contents = file.file.read()
    df = pd.read_csv(io.BytesIO(contents))
    preds, _ = model_manager.predict(df)
    df_out = df.copy()
    df_out["prediction"] = preds
    stream = io.StringIO()
    df_out.to_csv(stream, index=False)
    stream.seek(0)
    headers = {"Content-Disposition": f"attachment; filename=bulk_predictions.csv"}
    return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers=headers)

@api.get("/report")
def report(format: str = "csv", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(Prediction).filter(Prediction.user_id == current_user.id).order_by(Prediction.created_at.desc()).all()
    data = [
        {"id": r.id, "features": r.features, "prediction": r.prediction, "created_at": r.created_at.isoformat()} for r in rows
    ]
    if format == "json":
        return data
    df = pd.DataFrame(data)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    stream.seek(0)
    headers = {"Content-Disposition": f"attachment; filename=report.csv"}
    return StreamingResponse(iter([stream.getvalue()]), media_type="text/csv", headers=headers)

@api.get("/")
def api_root():
    return {"message": "Student Performance Prediction API", "endpoints": ["/api/auth/register", "/api/auth/login", "/api/predict", "/api/train", "/api/metrics", "/api/bulk_predict", "/api/report"]}

# Include API router first
app.include_router(api)

# Add a root endpoint for health check
@app.get("/")
def root():
    return {"message": "MarkMate API Server", "status": "running", "api_docs": "/docs", "api_root": "/api"}

# Mount frontend as static site (but this won't work on Render since we're API-only)
# FRONTEND_DIR = str((Path(__file__).resolve().parent.parent / "frontend").resolve())
# if not os.path.exists(FRONTEND_DIR):
#     # fallback if running from project root
#     FRONTEND_DIR = str((Path(__file__).resolve().parent.parent.parent / "frontend").resolve())
# app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
