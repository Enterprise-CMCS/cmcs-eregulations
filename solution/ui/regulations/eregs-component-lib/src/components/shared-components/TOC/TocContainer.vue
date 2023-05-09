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
const getTitlesArray = async () => {
    const titlesArray = await getTitles(props.apiUrl);
    titles.value = titlesArray;
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

watch(titles, (newVal) => {
    getTOCs(newVal);
});

// On load
getTitlesArray();
</script>

<template>
    <div>
        <div>{{ titles }}</div>
        <template v-for="(toc, i) in TOCs">
            <Toc :key="i" :structure="toc" />
        </template>
    </div>
</template>

<style></style>
