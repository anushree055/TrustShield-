"""Train the two small bundled demo ML models.
For production/research results, replace the seed CSVs with larger labelled datasets.
"""
from pathlib import Path
import re, ipaddress
from urllib.parse import urlparse
import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MODELS = ROOT / "models"
MODELS.mkdir(exist_ok=True)

WORDS = ["login","verify","secure","update","account","bank","banking","password","confirm","wallet","payment","signin","kyc","otp","bonus","prize"]
SHORT = ["bit.ly","tinyurl.com","t.co","goo.gl","ow.ly","is.gd","buff.ly","cutt.ly","tiny.cc"]
EXT = [".exe",".scr",".zip",".apk",".js"]

def url_features(url):
    if not re.match(r"^https?://", str(url), re.I): url = "http://" + str(url)
    p = urlparse(url); h = p.hostname or ""; path=p.path or ""
    try: ipaddress.ip_address(h); has_ip=1
    except: has_ip=0
    return [len(url),url.count('.'),url.count('-'),len(re.findall(r'[^A-Za-z0-9]',url)),int('@' in url),has_ip,int(p.scheme=='https'),max(0,h.count('.')-1),sum(w in url.lower() for w in WORDS),int(any(s in h.lower() for s in SHORT)),sum(c.isdigit() for c in h),int(any(path.lower().endswith(x) for x in EXT))]

def train_message():
    df = pd.read_csv(DATA / "message_training.csv")
    X_train,X_test,y_train,y_test=train_test_split(df.text,df.label,test_size=.25,random_state=42,stratify=df.label)
    model=Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2),min_df=1,max_features=5000)),("clf",LogisticRegression(max_iter=1000,class_weight="balanced",random_state=42))])
    model.fit(X_train,y_train)
    print("Message accuracy:", accuracy_score(y_test, model.predict(X_test)))
    joblib.dump(model, MODELS / "message_model.joblib")

def train_url():
    df=pd.read_csv(DATA / "url_training.csv")
    X=[url_features(u) for u in df.url]
    X_train,X_test,y_train,y_test=train_test_split(X,df.label,test_size=.25,random_state=42,stratify=df.label)
    model=RandomForestClassifier(n_estimators=160,max_depth=8,random_state=42,class_weight="balanced")
    model.fit(X_train,y_train)
    print("URL accuracy:", accuracy_score(y_test, model.predict(X_test)))
    joblib.dump(model, MODELS / "url_model.joblib")

if __name__ == "__main__":
    train_message(); train_url(); print("Saved models to", MODELS)
