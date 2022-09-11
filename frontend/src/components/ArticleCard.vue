<script setup lang="ts">
import { computed, ref } from 'vue';
import { Article, Emotion } from './models';

interface Props {
  article: Article;
  hideNegative: boolean;
}
const props = withDefaults(defineProps<Props>(), {});

const sentimentColour = (sentiment: number) => {
  if (sentiment > 0.25) return 'green';
  if (sentiment < -0.25) return 'red';
  return 'amber-12';
};

const sentimentDisplayValue = (sentiment: number, multiply = true) => {
  if (sentiment < 0) sentiment *= -1;
  const multiple = multiply ? 100 : 1;
  return (sentiment * multiple).toFixed(2);
};

const hideCard = () =>
  props.article.sentiment_title < 0 && props.hideNegative ? false : true;

// const todoCount = computed(() => props.todos.length);
</script>

<template>
  <q-card flat square bordered class="article-card">
    <div class="glass" :class="{ 'hide-card': hideCard() }"></div>
    <a :href="article.link">
      <!-- <img v-if="article.img.startsWith('http')" :src="article.img" /> -->

      <q-card-section>
        <div class="text-h6">{{ article.title }}</div>
        <div class="text-subtitle2">{{ article.article_time }}</div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        {{ article.summary }}
      </q-card-section>

      <q-card-section class="q-pt-none">
        <span class="text-subtitle2">Sentiment</span>
        <div class="q-mt-sm">
          <q-chip
            outline
            square
            :color="sentimentColour(article.sentiment_title)"
          >
            Title: {{ sentimentDisplayValue(article.sentiment_title) }}
          </q-chip>
          <q-chip
            outline
            square
            :color="sentimentColour(article.sentiment_summary)"
          >
            Summary: {{ sentimentDisplayValue(article.sentiment_summary) }}
          </q-chip>
          <q-chip
            outline
            square
            :color="sentimentColour(article.sentiment_article_title)"
          >
            Article title:
            {{ sentimentDisplayValue(article.sentiment_article_title) }}
          </q-chip>
          <q-chip
            outline
            square
            :color="sentimentColour(article.sentiment_text)"
          >
            Article text:
            {{ sentimentDisplayValue(article.sentiment_text, false) }}
          </q-chip>
        </div>
      </q-card-section>
    </a>
  </q-card>
</template>

<style lang="scss">
.article-card {
  min-width: 20%;
}

a {
  text-decoration: none;
}

.glass {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: rgba(193, 132, 132, 0.2);
  backdrop-filter: blur(6px);
  z-index: 99;
  height: 100%;
  width: 100%;
}

.hide-card {
  display: none;
}
</style>
