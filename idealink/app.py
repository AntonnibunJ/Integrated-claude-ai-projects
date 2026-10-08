import os, re, math, random, string
from collections import Counter
from functools import wraps
from flask import Flask, request, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.getenv("SECRET_KEY", "change-me")
CFG = dict(host=os.getenv("DB_HOST", "localhost"), user=os.getenv("DB_USER", "root"),
           password=os.getenv("DB_PASS", ""), database=os.getenv("DB_NAME", "idealink"))

def q(sql, args=(), one=False, write=False):
    c = mysql.connector.connect(**CFG); cur = c.cursor(dictionary=True)
    try:
        cur.execute(sql, args)
        if write:
            c.commit(); return cur.lastrowid
        return cur.fetchone() if one else cur.fetchall()
    finally:
        cur.close(); c.close()

# No contact details may travel through the platform.
BLOCK = re.compile(r"[\w.+-]+@[\w-]+\.\w+|\+?\d[\d\s-]{7,}\d|https?://\S+|www\.\S+|@\w{3,}", re.I)
clean = lambda t: BLOCK.sub("[hidden]", (t or "").strip())

STOP = set("the and for with that this are was were from have has can how our your you not but all any into more also than then them".split())
toks = lambda t: [w for w in re.findall(r"[a-z]{3,}", t.lower()) if w not in STOP]

def rank(text, rows, n=6):
    """TF-IDF cosine similarity between one problem statement and many."""
    docs = [toks(r["title"] + " " + r["statement"]) for r in rows]; qt = toks(text)
    df = Counter(w for d in docs + [qt] for w in set(d)); N = len(docs) + 1
    vec = lambda d: {w: c * (1 + math.log(N / df[w])) for w, c in Counter(d).items()}
    norm = lambda v: math.sqrt(sum(x * x for x in v.values())) or 1
    qv = vec(qt); qn = norm(qv); out = []
    for r, d in zip(rows, docs):
        v = vec(d); s = sum(qv[w] * v.get(w, 0) for w in qv) / (qn * norm(v))
        if s > 0.12: out.append({**r, "score": round(s * 100)})
    return sorted(out, key=lambda x: -x["score"])[:n]

def auth(f):
    @wraps(f)
    def w(*a, **k):
        if "uid" not in session: return jsonify(error="Please sign in first"), 401
        return f(*a, **k)
    return w

def err(m, c=400): return jsonify(error=m), c

@app.route("/")
def home(): return app.send_static_file("index.html")

@app.post("/api/register")
def register():
    d = request.json or {}; email = d.get("email", "").lower().strip()
    if not re.match(r"[^@\s]+@[^@\s]+\.\w+$", email) or len(d.get("password", "")) < 6:
        return err("Use a valid email and a password of 6+ characters")
    if q("SELECT id FROM users WHERE email=%s", (email,), one=True): return err("That email is already registered")
    pid = "IL-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    nick = clean(d.get("nickname"))[:40] or "Learner"
    session["uid"] = q("INSERT INTO users(email,pw,private_id,nickname) VALUES(%s,%s,%s,%s)",
                       (email, generate_password_hash(d["password"]), pid, nick), write=True)
    return jsonify(private_id=pid, nickname=nick)

@app.post("/api/login")
def login():
    d = request.json or {}
    u = q("SELECT * FROM users WHERE email=%s", ((d.get("email") or "").lower().strip(),), one=True)
    if not u or not check_password_hash(u["pw"], d.get("password", "")): return err("Email or password is incorrect", 401)
    session["uid"] = u["id"]; return jsonify(private_id=u["private_id"], nickname=u["nickname"])

@app.post("/api/logout")
def logout(): session.clear(); return jsonify(ok=1)

@app.get("/api/me")
@auth
def me(): return jsonify(q("SELECT private_id,nickname FROM users WHERE id=%s", (session["uid"],), one=True))

def matches_for(text, uid):
    rows = q("SELECT i.id idea_id,i.title,i.statement,u.id user_id,u.private_id,u.nickname FROM ideas i "
             "JOIN users u ON u.id=i.user_id WHERE i.user_id<>%s", (uid,))
    res = rank(text, rows)
    for r in res:
        r["statement"] = r["statement"][:160]
        c = q("SELECT status FROM connections WHERE from_user=%s AND to_user=%s AND idea_id=%s",
              (uid, r["user_id"], r["idea_id"]), one=True)
        r["connected"] = c["status"] if c else None; del r["user_id"]
    return res

@app.post("/api/ideas")
@auth
def add_idea():
    d = request.json or {}; t, s = clean(d.get("title"))[:140], clean(d.get("statement"))
    if len(t) < 4 or len(s) < 20: return err("Add a title and describe the problem in at least 20 characters")
    iid = q("INSERT INTO ideas(user_id,title,statement,tags) VALUES(%s,%s,%s,%s)",
            (session["uid"], t, s, clean(d.get("tags"))[:200]), write=True)
    return jsonify(id=iid, matches=matches_for(t + " " + s, session["uid"]))

@app.get("/api/ideas")
@auth
def my_ideas(): return jsonify(q("SELECT id,title,statement FROM ideas WHERE user_id=%s ORDER BY id DESC", (session["uid"],)))

@app.get("/api/ideas/<int:i>/matches")
@auth
def idea_matches(i):
    r = q("SELECT title,statement FROM ideas WHERE id=%s AND user_id=%s", (i, session["uid"]), one=True)
    return jsonify(matches_for(r["title"] + " " + r["statement"], session["uid"]) if r else [])

@app.post("/api/connect")
@auth
def connect():
    iid = (request.json or {}).get("idea_id")
    t = q("SELECT user_id FROM ideas WHERE id=%s", (iid,), one=True)
    if not t or t["user_id"] == session["uid"]: return err("That idea can't be connected to")
    try: q("INSERT INTO connections(from_user,to_user,idea_id) VALUES(%s,%s,%s)", (session["uid"], t["user_id"], iid), write=True)
    except mysql.connector.IntegrityError: return err("Request already sent")
    return jsonify(ok=1)

@app.get("/api/connections")
@auth
def conns():
    u = session["uid"]
    return jsonify(q("SELECT c.id,c.status,(c.to_user=%s) incoming,o.private_id,o.nickname,i.title FROM connections c "
                     "JOIN users o ON o.id=IF(c.from_user=%s,c.to_user,c.from_user) JOIN ideas i ON i.id=c.idea_id "
                     "WHERE %s IN (c.from_user,c.to_user) ORDER BY c.id DESC", (u, u, u)))

@app.post("/api/connections/<int:c>/accept")
@auth
def accept(c):
    q("UPDATE connections SET status='accepted' WHERE id=%s AND to_user=%s", (c, session["uid"]), write=True); return jsonify(ok=1)

def member(c):
    return q("SELECT id FROM connections WHERE id=%s AND status='accepted' AND %s IN (from_user,to_user)", (c, session["uid"]), one=True)

@app.route("/api/chat/<int:c>", methods=["GET", "POST"])
@auth
def chat(c):
    if not member(c): return err("Chat opens after the request is accepted", 403)
    if request.method == "POST":
        b = clean((request.json or {}).get("body"))[:1000]
        if b: q("INSERT INTO messages(conn_id,sender_id,body) VALUES(%s,%s,%s)", (c, session["uid"], b), write=True)
        return jsonify(ok=1)
    return jsonify(q("SELECT body,(sender_id=%s) mine,sent_at FROM messages WHERE conn_id=%s ORDER BY id", (session["uid"], c)))

@app.get("/api/trending")
@auth
def trending():
    rows = q("SELECT p.id,p.title,p.description,u.private_id,u.nickname,p.views,"
             "(SELECT COUNT(*) FROM likes l WHERE l.project_id=p.id) likes,"
             "(SELECT COUNT(*) FROM likes l WHERE l.project_id=p.id AND l.user_id=%s) liked,"
             "TIMESTAMPDIFF(HOUR,p.created_at,NOW()) age FROM projects p JOIN users u ON u.id=p.user_id", (session["uid"],))
    for r in rows: r["score"] = (r["likes"] * 3 + r["views"]) / (r["age"] + 2) ** 1.2
    return jsonify(sorted(rows, key=lambda r: -r["score"])[:20])

@app.post("/api/projects")
@auth
def add_project():
    d = request.json or {}; t, s = clean(d.get("title"))[:140], clean(d.get("description"))
    if len(t) < 4 or len(s) < 10: return err("Add a title and a short description")
    q("INSERT INTO projects(user_id,title,description) VALUES(%s,%s,%s)", (session["uid"], t, s), write=True); return jsonify(ok=1)

@app.post("/api/projects/<int:p>/like")
@auth
def like(p):
    if q("SELECT 1 x FROM likes WHERE project_id=%s AND user_id=%s", (p, session["uid"]), one=True):
        q("DELETE FROM likes WHERE project_id=%s AND user_id=%s", (p, session["uid"]), write=True)
    else: q("INSERT INTO likes VALUES(%s,%s)", (p, session["uid"]), write=True)
    return jsonify(ok=1)

@app.route("/api/tickets", methods=["GET", "POST"])
@auth
def tickets():
    if request.method == "POST":
        d = request.json or {}; s, t = clean(d.get("subject"))[:140], clean(d.get("details"))
        if len(s) < 4 or len(t) < 10: return err("Add a subject and a few details so we can help")
        q("INSERT INTO tickets(user_id,category,subject,details) VALUES(%s,%s,%s,%s)",
          (session["uid"], d.get("category", "other")[:30], s, t), write=True); return jsonify(ok=1)
    return jsonify(q("SELECT id,category,subject,status,reply FROM tickets WHERE user_id=%s ORDER BY id DESC", (session["uid"],)))

if __name__ == "__main__": app.run(debug=True)
