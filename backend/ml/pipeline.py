import os
import json
from typing import Dict, Tuple, Optional, List
import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import joblib

try:
    from xgboost import XGBClassifier  # type: ignore
    HAS_XGB = True
except Exception:
    HAS_XGB = False

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "students_sample.csv")
SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saved")
MODEL_PATH = os.path.join(SAVE_DIR, "model.pkl")
METRICS_PATH = os.path.join(SAVE_DIR, "metrics.json")

os.makedirs(SAVE_DIR, exist_ok=True)

FEATURES = [
    "study_hours", "attendance", "previous_marks", "participation", "internet_access", "parental_education"
]
TARGET = "passed"

class ModelManager:
    def __init__(self) -> None:
        self.model: Optional[Pipeline] = None
        self.metrics: Optional[Dict[str, float]] = None
        self._load()

    def _load(self) -> None:
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                if os.path.exists(METRICS_PATH):
                    with open(METRICS_PATH, "r") as f:
                        self.metrics = json.load(f)
            except Exception:
                self.model = None

    def ensure_data(self) -> pd.DataFrame:
        if not os.path.exists(DATA_PATH):
            # Create a tiny synthetic dataset if missing
            rng = np.random.default_rng(42)
            n = 200
            df = pd.DataFrame({
                "study_hours": rng.normal(3, 1.2, n).clip(0, 10),
                "attendance": rng.normal(80, 10, n).clip(30, 100),
                "previous_marks": rng.normal(60, 15, n).clip(0, 100),
                "participation": rng.integers(0, 11, n),
                "internet_access": rng.integers(0, 2, n),
                "parental_education": rng.integers(0, 5, n),
            })
            # Rule-based pass
            score = 0.4*df["previous_marks"] + 0.3*df["attendance"] + 0.2*df["study_hours"]*10 + 0.1*df["participation"]*10
            thresh = np.percentile(score, 55)
            df[TARGET] = (score >= thresh).astype(int)
            os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
            df.to_csv(DATA_PATH, index=False)
        return pd.read_csv(DATA_PATH)

    def build_preprocessor(self) -> ColumnTransformer:
        numeric_features = FEATURES
        preproc = ColumnTransformer([
            ("num", StandardScaler(), numeric_features)
        ], remainder="drop")
        return preproc

    def candidate_models(self) -> Dict[str, object]:
        models = {
            "logreg": LogisticRegression(max_iter=1000),
            "rf": RandomForestClassifier(n_estimators=200, random_state=42)
        }
        if HAS_XGB:
            models["xgb"] = XGBClassifier(n_estimators=200, learning_rate=0.1, max_depth=4, subsample=0.9, colsample_bytree=0.9, eval_metric="logloss")
        return models

    def train_and_save(self) -> Tuple[str, Dict[str, float]]:
        df = self.ensure_data()
        X = df[FEATURES]
        y = df[TARGET]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
        preproc = self.build_preprocessor()

        best_name = None
        best_f1 = -1.0
        best_pipe: Optional[Pipeline] = None
        best_metrics: Dict[str, float] = {}

        for name, clf in self.candidate_models().items():
            pipe = Pipeline([
                ("pre", preproc),
                ("clf", clf)
            ])
            pipe.fit(X_train, y_train)
            preds = pipe.predict(X_test)
            acc = accuracy_score(y_test, preds)
            prec = precision_score(y_test, preds, zero_division=0)
            rec = recall_score(y_test, preds, zero_division=0)
            f1 = f1_score(y_test, preds, zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_name = name
                best_pipe = pipe
                best_metrics = {"accuracy": float(acc), "precision": float(prec), "recall": float(rec), "f1": float(f1)}

        assert best_pipe is not None and best_name is not None
        joblib.dump(best_pipe, MODEL_PATH)
        with open(METRICS_PATH, "w") as f:
            json.dump(best_metrics, f)
        self.model = best_pipe
        self.metrics = best_metrics
        return best_name, best_metrics

    def predict(self, df: pd.DataFrame):
        if self.model is None:
            # lazy train
            self.train_and_save()
        assert self.model is not None
        preds = self.model.predict(df[FEATURES])
        prob = None
        try:
            proba = self.model.predict_proba(df[FEATURES])
            prob = [{"0": float(p[0]), "1": float(p[1])} for p in proba]
        except Exception:
            prob = None
        return preds, prob
