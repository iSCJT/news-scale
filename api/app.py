import os
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()


# init api
app = Flask(__name__)
CORS(app)

# print(os.getenv('DEV_DATABASE_URL'))

# database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DEV_DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Scrape(db.Model):
    __tablename__ = 'scrapes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True), nullable=False)
    success = db.Column(db.Boolean, default=False)
    articles = db.relationship('Article', back_populates='scrapes')


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scrape_id = db.Column(db.Integer, db.ForeignKey(
        'scrapes.id'), nullable=False)
    scrapes = db.relationship('Scrape', back_populates='articles')
    section = db.Column(db.String(20), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    title = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    img = db.Column(db.Text, nullable=False)
    link = db.Column(db.Text, nullable=False)
    article_title = db.Column(db.Text, nullable=False)
    article_time = db.Column(db.DateTime(timezone=True), nullable=True)
    article_text = db.Column(db.Text, nullable=False)
    sentiment_title = db.Column(db.Float, nullable=False)
    sentiment_summary = db.Column(db.Float, nullable=False)
    sentiment_article_title = db.Column(db.Float, nullable=False)
    sentiment_text = db.Column(db.Float, nullable=False)
    emotions = db.relationship('Emotion', back_populates='articles')


class Emotion(db.Model):
    __tablename__ = 'emotions'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    article_id = db.Column(db.Integer, db.ForeignKey(
        'articles.id'), nullable=False)
    articles = db.relationship('Article', back_populates='emotions')
    item = db.Column(db.String(30), nullable=False)
    emotion = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Float, nullable=False)


scrapes = Scrape.query.all()

articles = Article.query.all()
emotions = Emotion.query.all()


class ScrapeData(db.Model):
    __table__ = db.Table('scrape_data', db.metadata,
                         db.Column('id', db.Integer, primary_key=True),
                         autoload_with=db.engine
                         )


scrape_data = ScrapeData.query.order_by(ScrapeData.id.desc()).first()

# print(scrape_data)


@ app.route('/', methods=['GET'])
def get():
    return render_template('index.html', scrapes=scrapes, articles=articles, emotions=emotions)


@ app.route('/json', methods=['GET'])
def json():
    # return jsonify(scrape_data)
    response = {
        'id': scrape_data.id,
        'start_time': scrape_data.start_time,
        'end_time': scrape_data.end_time,
        'success': scrape_data.success,
        'articles': scrape_data.articles
    }

    return jsonify(response)


# run server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # <==== This creates db object
    app.run(debug=True, port=8080)
