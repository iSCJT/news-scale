from traceback import StackSummary
import scrape
import time
import datetime
from settings import region
import models

# Takes a story and builds an article model


def prepare_articles(story) -> dict:
    # Emotions are a separate table so we build a list of emotion models for
    # the 4 different emotion items
    emotions_model_list = prepare_emotions(
        'emotion-title', story['emotion-title'])

    emotions_model_list.extend(prepare_emotions(
        'emotion-summary', story['emotion-summary']))

    emotions_model_list.extend(prepare_emotions(
        'emotion-article-title', story['emotion-article-title']))

    emotions_model_list.extend(prepare_emotions(
        'emotion-text', story['emotion-text']))

    return models.Article(
        id=None, section=story['section'], position=story['position'],
        title=story['title'], summary=story['summary'],
        img=story['img'], link=story['link'], article_title=story['article-title'],
        article_time=story['article-time'], article_text=story['article-text'],
        sentiment_title=story['sentiment-title'], sentiment_summary=story['sentiment-summary'],
        sentiment_article_title=story['sentiment-article-title'], sentiment_text=story['sentiment-text'],
        emotions=emotions_model_list
    )

# Iterates over the emotion dictionaries and returns a list of emotion models


def prepare_emotions(item, emotions) -> list:
    model_list = []

    for key, value in emotions.items():
        e = models.Emotion(id=None, item=item,
                           emotion=key, score=value)
        model_list.append(e)

    return model_list


# Trigger a scrape of the bbc homepage, the bbc homepage loads 'duplicate' top news
# for each country of the UK and then a general domestic block.  Based on settings
# it hides all the other versions.  We'll just pass the generic value here but other
# options are listed in the settings file.

scrape_success = False
scrape_start = datetime.datetime.fromtimestamp(time.time())
print('Scrape started at: %s' % scrape_start)

# Hacky catch all error exception
# TODO: Proper error catching and output within class
try:
    bbc = scrape.bbc(region['domestic'])
    scrape_success = True

    # === Used during testing to check result format ===
    # with open('top_stories.html', 'w') as f:
    #     f.write(str(bbc.top_stories))

except Exception as e:
    print('Scrape failed: %s' % e)
    pass

scrape_end = datetime.datetime.fromtimestamp(time.time())
# Save the scrape header to database

# Grab top stories array
top_stories = bbc.top_stories

article_model_list = []

# Loop through stories and generate model lists
for story in top_stories:
    article_model_list.append(prepare_articles(story))

# Generate the top level scrape model instance that includes articles model list
scrape_attempt = models.Scrape(
    id=None, start_time=scrape_start, end_time=scrape_end, success=scrape_success, articles=article_model_list)

# Add model to the open session
models.session.add(scrape_attempt)

# Commit scrape to database
models.session.commit()

# TODO: need to check dave was successful
if scrape_success == True:
    print('Scrape successfully completed on %s' % scrape_end)
