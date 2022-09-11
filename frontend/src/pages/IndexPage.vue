<script setup>
import { ref } from 'vue';
import ArticleCard from '../components/ArticleCard.vue';

const latestScrape = ref({});

const loadLatestScrape = async () => {
  latestScrape.value = await fetch('http://localhost:8080/json').then((r) =>
    r.json()
  );
  // data.value = {
  //   status: response.status,
  //   statusText: response.statusText,
  //   data: response.body,
  // };
  // console.log(response);
  // data.res = response;
  // return response;
};

loadLatestScrape();

const hideNegative = ref(true);
</script>

<template>
  <q-page class="row items-center align-start q-pa-md">
    <div class="row justify-between" style="width: 100%">
      <q-toggle
        v-model="hideNegative"
        color="red"
        label="Hide negative articles"
        left-label
      />
      <span>Last scraped: {{ latestScrape.start_time }}</span>
    </div>
    <div class="row justify-start">
      <ArticleCard
        v-for="article in latestScrape.articles"
        :key="article.id"
        :article="article"
        class="col-4 q-ma-md"
        :hideNegative="hideNegative"
      />
    </div>
  </q-page>
</template>

<style lang="scss">
a {
  color: $dark;
}
</style>
