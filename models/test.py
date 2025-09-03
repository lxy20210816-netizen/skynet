from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone, timedelta

Base = declarative_base()

# 定义表
class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(BigInteger)               # 原始时间戳
    time_local = Column(DateTime)                # 日本当地时间
    title = Column(String(255))
    link = Column(String(500))
    summary = Column(Text)
    content = Column(Text)

# 创建数据库连接
engine = create_engine(
    "mysql+pymysql://root:123456@127.0.0.1:3306/testdb?charset=utf8mb4",
    echo=False
)

# 创建表
Base.metadata.create_all(engine)

# 创建 session
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 假设爬虫拿到的数据
raw_timestamp = 1725352312   # 例如：Unix 时间戳
japan_tz = timezone(timedelta(hours=9))
time_local = datetime.fromtimestamp(raw_timestamp, tz=japan_tz)

article = Article(
    timestamp=raw_timestamp,
    time_local=time_local,
    title="日本新闻标题",
    link="https://example.com/article/123",
    summary="这是摘要",
    content="这是正文内容"
)

session.add(article)
session.commit()
session.close()
