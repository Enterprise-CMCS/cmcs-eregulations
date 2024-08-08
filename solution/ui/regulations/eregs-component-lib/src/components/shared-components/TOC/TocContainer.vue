<script setup>
import { provide, reactive, ref, watch } from "vue";

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
const getTitlesArray = async () => {
    const titlesArray = await getTitles({ apiUrl: props.apiUrl });
    const formattedTitleNamesArray = titlesArray.map(
        (title) => `Title ${title}`
    );
    titles.value = formattedTitleNamesArray;
};

// Table of Contents for each title
const TOCs = ref([]);
const getTOCs = async (titlesArr) => {
    const tocArray = await Promise.all(
        titlesArr.map(async (title) => {
            const tocStruct = await getTOC({ title, apiUrl: props.apiUrl });
            return tocStruct;
        })
    );

    TOCs.value = tocArray;
};

watch(titles, (newArr) => {
    const unformattedTitles = newArr.map((title) => title.split(" ")[1]);
    getTOCs(unformattedTitles);
});

// tab state, etc
const selectedTitle = ref(0);

// On load
getTitlesArray();
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
