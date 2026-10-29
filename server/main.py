"""
个人网站后端 - FastAPI + SQLite
运行：uvicorn main:app --reload --port 8010
"""
import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import bcrypt
from jose import jwt, JWTError
from typing import Optional

# ========== 配置 ==========
SECRET_KEY = "liwei-portfolio-secret-key-change-in-production-2026"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
DATABASE_URL = "sqlite:///./portfolio.db"

# ========== 数据库 ==========
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), default="李维")
    role = Column(String(100), default="物联网工程 · 嵌入式 / 硬件方向")
    lead = Column(Text, default="")
    email = Column(String(100), default="1932287285@qq.com")
    github = Column(String(200), default="https://github.com/")
    wechat = Column(String(100), default="")
    stat1_num = Column(String(20), default="3+")
    stat1_label = Column(String(50), default="学科竞赛经历")
    stat2_num = Column(String(20), default="10+")
    stat2_label = Column(String(50), default="动手小项目")
    stat3_num = Column(String(20), default="2")
    stat3_label = Column(String(50), default="在研大创项目")
    about = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow)


class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True)
    category = Column(String(50))  # 嵌入式/硬件、软件开发、工具/其他
    name = Column(String(100))
    level = Column(Integer)  # 0-100
    sort = Column(Integer, default=0)


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    year = Column(String(10))
    title = Column(String(200))
    description = Column(Text)
    tags = Column(String(200))  # 逗号分隔
    sort = Column(Integer, default=0)


class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True)
    date = Column(String(20))
    title = Column(String(200))
    summary = Column(Text)
    content = Column(Text, default="")
    sort = Column(Integer, default=0)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    nickname = Column(String(50))
    contact = Column(String(100), default="")
    content = Column(Text)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== 鉴权 ==========
def create_token(username: str) -> str:
    payload = {"sub": username, "exp": datetime.utcnow().timestamp() + 86400}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def require_admin(token: str = Depends(__import__("fastapi").security.OAuth2PasswordBearer(tokenUrl="/api/admin/login"))):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("sub") != ADMIN_USERNAME:
            raise JWTError()
    except JWTError:
        raise HTTPException(status_code=401, detail="未授权")
    return True


# ========== Pydantic ==========
class LoginIn(BaseModel):
    username: str
    password: str


class ProjectIn(BaseModel):
    year: str
    title: str
    description: str
    tags: str = ""


class BlogIn(BaseModel):
    date: str
    title: str
    summary: str
    content: str = ""


class MessageIn(BaseModel):
    nickname: str
    contact: str = ""
    content: str


# ========== App ==========
app = FastAPI(title="李维个人网站API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_if_empty(db: Session):
    """首次启动灌入初始数据（和原静态页一致）"""
    if db.query(Profile).first() is None:
        db.add(Profile(
            about="我是一名物联网工程专业的大三学生，平时泡在实验室和面包板之间。从51单片机点灯开始，慢慢玩到ESP32、传感器组网和简单的上位机。"
        ))
    if db.query(Skill).count() == 0:
        skills = [
            ("嵌入式 / 硬件", "C / 51 单片机", 85, 1),
            ("嵌入式 / 硬件", "ESP32 / Arduino", 80, 2),
            ("嵌入式 / 硬件", "传感器 / 电路焊接", 75, 3),
            ("嵌入式 / 硬件", "立创EDA / 原理图", 55, 4),
            ("软件开发", "Python", 72, 5),
            ("软件开发", "HTML / CSS / JS", 68, 6),
            ("软件开发", "Java / SpringBoot", 50, 7),
            ("软件开发", "Vue3", 45, 8),
            ("工具 / 其他", "Git / GitHub", 70, 9),
            ("工具 / 其他", "Keil / VS Code", 82, 10),
            ("工具 / 其他", "Linux 基础命令", 55, 11),
            ("工具 / 其他", "AI 辅助开发", 85, 12),
        ]
        for cat, name, lv, s in skills:
            db.add(Skill(category=cat, name=name, level=lv, sort=s))
    if db.query(Project).count() == 0:
        projects = [
            (2025, "基于 ESP32-CAM 的远程监控", "用 ESP32-CAM 搭建的网络摄像头，实现网页端实时查看与移动侦测，负责硬件接线与固件调试。", "ESP32,摄像头,IoT", 1),
            (2024, "TI 杯电子设计竞赛作品", "信号类赛题，基于单片机实现信号采集、运放调理与输出，完成从原理图到实物联调的全流程。", "C,单片机,运放电路", 2),
            (2025, "个人作品集网站", "就是你现在看到的这个站。深色星空主题，前后端分离，带留言板和管理后台。", "FastAPI,Vue3,Canvas", 3),
            (2025, "大学生创新训练项目", "在研项目，负责传感器节点的固件开发与数据上报，配套简单的上位机展示页面。", "大创,传感器,嵌入式", 4),
        ]
        for y, t, d, tg, s in projects:
            db.add(Project(year=str(y), title=t, description=d, tags=tg, sort=s))
    if db.query(Blog).count() == 0:
        blogs = [
            ("2025-10-20", "第一次用 AI 从 0 做一个网站", "从写 PRD 到部署上线，记录我如何把一句想法变成一个能访问的网页。", "", 1),
            ("2025-09-12", "ESP32 上手踩坑笔记", "供电、烧录、串口乱码……把第一次玩 ESP32 踩过的坑整理成一份清单。", "", 2),
            ("2025-08-03", "电赛备赛：我是怎么调 bug 的", "从分不清前后端，到学会看状态码和报错信息，一点拙见。", "", 3),
        ]
        for d, t, sm, ct, s in blogs:
            db.add(Blog(date=d, title=t, summary=sm, content=ct, sort=s))
    db.commit()


@app.on_event("startup")
def startup():
    db = SessionLocal()
    seed_if_empty(db)
    db.close()


# ========== 公开API ==========
@app.get("/api/profile")
def get_profile(db: Session = Depends(get_db)):
    p = db.query(Profile).first()
    return {
        "name": p.name, "role": p.role, "lead": p.lead, "email": p.email,
        "github": p.github, "wechat": p.wechat,
        "stats": [
            {"num": p.stat1_num, "label": p.stat1_label},
            {"num": p.stat2_num, "label": p.stat2_label},
            {"num": p.stat3_num, "label": p.stat3_label},
        ],
        "about": p.about,
    }


@app.get("/api/skills")
def get_skills(db: Session = Depends(get_db)):
    rows = db.query(Skill).order_by(Skill.sort).all()
    cats = {}
    for r in rows:
        cats.setdefault(r.category, []).append({"name": r.name, "level": r.level})
    return cats


@app.get("/api/projects")
def get_projects(db: Session = Depends(get_db)):
    rows = db.query(Project).order_by(Project.sort).all()
    return [{"id": r.id, "year": r.year, "title": r.title, "description": r.description,
             "tags": [t.strip() for t in r.tags.split(",") if t.strip()]} for r in rows]


@app.get("/api/blogs")
def get_blogs(db: Session = Depends(get_db)):
    rows = db.query(Blog).order_by(Blog.sort).all()
    return [{"id": r.id, "date": r.date, "title": r.title, "summary": r.summary} for r in rows]


@app.get("/api/messages")
def get_messages(db: Session = Depends(get_db)):
    """只返回已审核通过的留言"""
    rows = db.query(Message).filter(Message.approved == True).order_by(Message.created_at.desc()).all()
    return [{"id": r.id, "nickname": r.nickname, "content": r.content,
             "created_at": r.created_at.strftime("%Y-%m-%d %H:%M")} for r in rows]


@app.post("/api/messages")
def post_message(body: MessageIn, db: Session = Depends(get_db)):
    m = Message(nickname=body.nickname, contact=body.contact, content=body.content, approved=False)
    db.add(m)
    db.commit()
    return {"msg": "留言提交成功，审核后展示"}


# ========== 管理API ==========
@app.post("/api/admin/login")
def admin_login(body: LoginIn):
    if body.username == ADMIN_USERNAME and bcrypt.checkpw(body.password.encode(), ADMIN_PASSWORD_HASH.encode()):
        return {"token": create_token(ADMIN_USERNAME)}
    raise HTTPException(status_code=400, detail="用户名或密码错误")


@app.get("/api/admin/messages")
def admin_list_messages(db: Session = Depends(get_db), _=Depends(require_admin)):
    rows = db.query(Message).order_by(Message.created_at.desc()).all()
    return [{"id": r.id, "nickname": r.nickname, "contact": r.contact, "content": r.content,
             "approved": r.approved, "created_at": r.created_at.strftime("%Y-%m-%d %H:%M")} for r in rows]


@app.post("/api/admin/messages/{mid}/approve")
def approve_message(mid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    m = db.query(Message).get(mid)
    if not m: raise HTTPException(404, "留言不存在")
    m.approved = True
    db.commit()
    return {"msg": "已通过"}


@app.delete("/api/admin/messages/{mid}")
def del_message(mid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    m = db.query(Message).get(mid)
    if m: db.delete(m); db.commit()
    return {"msg": "已删除"}


@app.post("/api/admin/projects")
def add_project(body: ProjectIn, db: Session = Depends(get_db), _=Depends(require_admin)):
    p = Project(year=body.year, title=body.title, description=body.description, tags=body.tags)
    db.add(p); db.commit(); db.refresh(p)
    return p


@app.delete("/api/admin/projects/{pid}")
def del_project(pid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    p = db.query(Project).get(pid)
    if p: db.delete(p); db.commit()
    return {"msg": "已删除"}


@app.post("/api/admin/blogs")
def add_blog(body: BlogIn, db: Session = Depends(get_db), _=Depends(require_admin)):
    b = Blog(date=body.date, title=body.title, summary=body.summary, content=body.content)
    db.add(b); db.commit(); db.refresh(b)
    return b


@app.delete("/api/admin/blogs/{bid}")
def del_blog(bid: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    b = db.query(Blog).get(bid)
    if b: db.delete(b); db.commit()
    return {"msg": "已删除"}


# ========== 静态文件托管 ==========
@app.get("/")
def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "index.html"))


@app.get("/admin")
def admin_page():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "admin.html"))


@app.get("/admin.html")
def admin_page_html():
    return FileResponse(os.path.join(os.path.dirname(__file__), "..", "admin.html"))


app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..")), name="static")
