
from sqlalchemy import create_engine, Column, ForeignKey, Boolean, Integer, BigInteger, Float, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy_utils import database_exists, create_database
from settings import postgres as settings

url = settings['url'] if settings['environment'] == 'prod' else settings['dev_url']

# if not database_exists(url):
#     create_database(url)

db = create_engine(url, pool_size=50, echo=False)

session = sessionmaker(bind=db)()

Base = declarative_base()


class Scrape(Base):
    __tablename__ = 'scrapes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    success = Column(Boolean, default=False)
    articles = relationship('Article', back_populates='scrapes')


class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    scrape_id = Column(Integer, ForeignKey('scrapes.id'), nullable=False)
    scrapes = relationship('Scrape', back_populates='articles')
    section = Column(String(20), nullable=False)
    position = Column(Integer, nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    img = Column(Text, nullable=False)
    link = Column(Text, nullable=False)
    article_title = Column(Text, nullable=False)
    article_time = Column(DateTime(timezone=True), nullable=True)
    article_text = Column(Text, nullable=False)
    sentiment_title = Column(Float, nullable=False)
    sentiment_summary = Column(Float, nullable=False)
    sentiment_article_title = Column(Float, nullable=False)
    sentiment_text = Column(Float, nullable=False)
    emotions = relationship('Emotion', back_populates='articles')


class Emotion(Base):
    __tablename__ = 'emotions'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)
    articles = relationship('Article', back_populates='emotions')
    item = Column(String(30), nullable=False)
    emotion = Column(String(20), nullable=False)
    score = Column(Float, nullable=False)


def create():
    Base.metadata.create_all(db)


create()
