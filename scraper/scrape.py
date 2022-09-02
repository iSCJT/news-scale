from bs4 import BeautifulSoup as bs
import requests
from transformers import pipeline
sentiment_analysis = pipeline("sentiment-analysis")
emotion_analysis = pipeline("text-classification",
                            model='bhadresh-savani/distilbert-base-uncased-emotion', top_k=9)


headers = {
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15'}


class bbc:
    def __init__(self, region):
        # Fetches bbc news home page
        self.front_page = requests.get(
            'https://www.bbc.co.uk/news', headers=headers)

        # Grabs just the content html
        self.html = self.front_page.content

        # Parses the content using beautiful soup
        self.soup = bs(self.html, 'html.parser')

        # Finds the main body of the home page that contains articles
        self.body = self.get_body()

        # Grabs processed top stories data
        self.top_stories = self.get_top_stories(region)

        # PLACEHOLDER FUNCTIONS FOR FUTURE DEVELOPMENT
        # self.must_see = self.get_must_see()
        # self.most_watched = self.get_most_watched()
        # self.full_story = self.get_full_story()
        # self.most_read = self.get_most_read()
        # self.newsbeat = self.get_newsbeat()
        # self.sport = self.get_sport()

# === FETCHES VISIBLE CONTENT FROM MAIN STORIES CONTAINER ===
    def get_body(self) -> list:
        content = self.soup.find('div', id='latest-stories-tab-container')

        # BBC website has duplicates of articles and then hides them
        # based on settings or device, this removes the duplicates from our results
        hidden = self.soup.find_all(
            'div', style='display:none;visibility:hidden;')
        for div in hidden:
            div.decompose()

        return content

# === FETCHES ARTICLES FROM TOP STORIES SECTION ===
    def get_top_stories(self, region) -> list:
        articles = []

        # Get top stories but ignoring live blocks for now
        stories = self.body.find(
            'div', id='nw-c-topstories-' + region).find_all(class_='nw-c-promo')

        # If stories found then loop through them and extract individual fields
        if len(stories) > 0:
            for i in range(len(stories)):
                story = stories[i]

                # Build a list of processed story/article information
                articles.append(self.process_article(
                    story, 'top-stories', i + 1))
        return articles

# === PROCESSES INDIVIDUAL ARTICLES AND RETURNS FIELDS AND SENTIMENT ANALYSIS ===
    def process_article(self, article, section, position) -> dict:
        # Sets up details dictionary
        details = {'section': section, 'position': position}

        # Grabs title for the article from home page
        title = article.find(class_='gs-c-promo-heading__title').text
        details['title'] = title

        # Grabs the summary for the article from home page
        summary = article.find(class_='gs-c-promo-summary').text
        details['summary'] = summary

        # Grabs image used on homepage
        img = article.find(class_='gs-c-promo-image').img['src']

        # If 'image' is a video we need to get it in a different way
        if not img:
            img = article.find('img', class_='p_holding_image')

        details['img'] = img

        # Grabs link to the article's page
        article_link = article.find('a', class_='gs-c-promo-heading')

        link = 'https://www.bbc.co.uk' + article_link['href']
        details['link'] = link

        # Scrape the article page and return the data we want
        page_details = self.get_article_page(link)

        # Merge the dictionaries
        details |= page_details

        # Extract fields that need sentiment analysis to variables
        article_title = details['article-title']
        article_text_array = details['article-text-array']

        # Run sentiment analysis on required fields
        details['sentiment-title'] = self.sentiment_format(
            sentiment_analysis(title))
        details['sentiment-summary'] = self.sentiment_format(
            sentiment_analysis(summary))
        details['sentiment-article-title'] = self.sentiment_format(
            sentiment_analysis(article_title))

        # Run sentiment analysis for the text array
        text_sentiment = sentiment_analysis(article_text_array)

        # We'll now work out a combined sentiment from the article paragraphs
        total_sentiment = 0

        for sentiment in text_sentiment:
            if sentiment['label'] == 'POSITIVE':
                total_sentiment += sentiment['score']
            elif sentiment['label'] == 'NEGATIVE':
                total_sentiment -= sentiment['score']

        # And then save the mean so that the number is more comparable to other fields
        # TODO: Getting divide by zero errors here
        # details['sentiment-text'] = total_sentiment / len(article_text_array)
        details['sentiment-text'] = total_sentiment

        # Run emotion analysis on required fields
        details['emotion-title'] = self.emotion_format(
            emotion_analysis(title))
        details['emotion-summary'] = self.emotion_format(
            emotion_analysis(summary))
        details['emotion-article-title'] = self.emotion_format(
            emotion_analysis(article_title))

        # Emotions are 1 to n so need to process a little differently to sentiment
        total_emotions = {}
        text_emotions = emotion_analysis(article_text_array)

        # We loop through the result for each paragraph
        for emotions in text_emotions:
            # And then the individual emotions for that paragraph
            for emotion in emotions:
                # We then total the scores for each emotions for all paragraphs combined
                if emotion['label'] in total_emotions:
                    total_emotions[emotion['label']] += emotion['score']
                else:
                    total_emotions[emotion['label']] = emotion['score']

        # Then loop through totals to save a mean emotion score so more comparable
        for emotion in total_emotions:
            total_emotions[emotion] /= len(text_emotions)

        # Save the final emotions list to our dictionary
        details['emotion-text'] = total_emotions

        # Remove the text array field as we don't want to save it to the database
        details.pop('article-text-array')

        return details

# === GRABS DETAILS FROM INDIVIDUAL ARTICLE PAGE ===
    def get_article_page(self, link) -> dict:

        article_details = {}

        # Grab the article page
        article_page = requests.get(link, headers=headers)

        # Grab the html content from the page
        article_html = article_page.content

        # Parse the content using beautiful soup
        article_soup = bs(article_html, 'html.parser')

        # The title often differs between the homepage and article page so we grab it again
        article_title = article_soup.find('h1').text
        article_details['article-title'] = article_title

        # Grab the time field from the article
        article_time = article_soup.time

        # Some article types don't have the datetime parameter and rely instead on
        # purely a text value e.g. '54 mins ago', we have to ignore these
        try:
            article_details['article-time'] = article_time['datetime']
        except Exception:
            pass

        # Grab the body of the article, it comes through as separate paragraphs so
        # we join these with a new line character but also keep hold of the list as
        # there's a character limit on the sentiment analysis so we process the paragraphs separate

        article_text = [p.text for p in article_soup.article.find_all(
            'p', class_='ssrcss-1q0x1qg-Paragraph eq5iqo00')]

        # Some bbc sport articles have a different layout
        if not article_text:
            article_text = [p.text for p in article_soup.find(
                'div', class_='qa-story-body').p]
        article_details['article-text'] = ('\n').join(article_text)
        article_details['article-text-array'] = article_text

        return article_details


# === FORMATS SENTIMENT INTO A SINGULAR VALUE ===

    def sentiment_format(self, sentiment) -> float:
        score = 0

        # Sentiment comes through wrapped in a list
        result = sentiment[0]

        # Returns a positive or negative score based on the label
        if result['label'] == 'POSITIVE':
            score += result['score']
        elif result['label'] == 'NEGATIVE':
            score -= result['score']

        return score

# === FORMATS EMOTIONS INTO A DICTIONARY WITH A SINGULAR SCORE PER EMOTION ===
    def emotion_format(self, emotions) -> dict:
        formatted = {}

        # Emotions come through in a list, we just want the dictionaries
        emotions = emotions[0]

        for emotion in emotions:
            if emotion['label'] in formatted:
                formatted[emotion['label']] += emotion['score']
            else:
                formatted[emotion['label']] = emotion['score']
        return formatted


# === PLACEHOLDERS FOR FUTURE DEVELOPMENT ===
    # def get_must_see(self) -> list:
    #     return self.body.find('div', class_='nw-c-must-see')

    # def get_most_watched(self) -> list:
    #     return self.body.find('div', class_='nw-c-most-watched')

    # def get_full_story(self) -> list:
    #     return self.body.find('div', class_='nw-c-full-story')

    # def get_most_read(self) -> list:
    #     return self.body.find('div', class_='nw-c-most-read')

    # def get_newsbeat(self) -> list:
    #     return self.body.find('div', class_='nw-c-Newsbeat')

    # def get_sport(self) -> list:
    #     return self.body.find('div', class_='nw-c-sport')
