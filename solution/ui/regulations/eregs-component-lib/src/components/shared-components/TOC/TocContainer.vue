<script>
const getTitlesArray = async ({ apiUrl, titles }) => {
    const titlesArray = await getTitles({ apiUrl });
    const formattedTitleNamesArray = titlesArray.map(
        (title) => `Title ${title}`
    );
    titles.value = formattedTitleNamesArray;
};

const getTOCs = async ({ apiUrl, titlesArr, TOCs }) => {
    const tocArray = await Promise.all(
        titlesArr.map(async (title) => {
            const tocStruct = await getTOC({ title, apiUrl });
            return tocStruct;
        })
    );

    TOCs.value = tocArray;
};

export default { getTitlesArray, getTOCs };
</script>

<script setup>
import { provide, ref, watch } from "vue";

import { getTitles, getTOC } from "utilities/api";

import Toc from "sharedComponents/TOC/Toc.vue";

const props = defineProps({
    apiUrl: {
        type: String,
        default: undefined,
    },
    homeUrl: {
        type: String,
        default: undefined,
    },
});

// allow non-reactive prop to be available to deeply nested children
provide("homeUrl", props.homeUrl);

// Titles
const titles = ref([]);

// Table of Contents for each title
const TOCs = ref([]);

watch(titles, (newArr) => {
    const unformattedTitles = newArr.map((title) => title.split(" ")[1]);
    getTOCs({ apiUrl: props.apiUrl, titlesArr: unformattedTitles, TOCs });
});

// tab state, etc
const selectedTitle = ref(0);

// On load
getTitlesArray({ apiUrl: props.apiUrl, titles });
</script>

<template>
    <div class="toc__container">
        <v-tabs v-model="selectedTitle">
            <v-tab v-for="(title, i) in titles" :key="i" tabindex="0">
                {{ title }}
            </v-tab>
        </v-tabs>
        <v-window v-model="selectedTitle" dark>
            <v-window-item v-for="(title, i) in titles" :key="i">
                <template v-if="TOCs[i]">
                    <Toc :structure="TOCs[i]" />
                </template>
            </v-window-item>
        </v-window>
    </div>
</template>

<style></style>
