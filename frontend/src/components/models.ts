export interface Article {
  id: number;
  position: number;
  section: string;
  title: string;
  summary: string;
  img: string;
  link: string;
  article_title: string;
  article_time: string;
  article_text: string;
  sentiment_title: number;
  sentiment_summary: number;
  sentiment_article_title: number;
  sentiment_text: number;
  scrape_id: number;
  emotions: Emotion[];
}

export interface Emotion {
  id: number;
  article_id: number;
  item: number;
  emotion: string;
  score: number;
}
