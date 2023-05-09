<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import { getTitles, getTOC } from "utilities/api";

import Toc from "sharedComponents/TOC/Toc.vue";

const props = defineProps({
    apiUrl: {
        type: String,
        default: undefined,
    },
});

// Titles
const titles = ref([]);
const getTitlesArray = async () => {
    const titlesArray = await getTitles(props.apiUrl);
    titles.value = titlesArray;
};

// Table of Contents for each title
const TOCs = ref([]);
const getTOCs = async (titles) => {
    const tocArray = await Promise.all(
        titles.map(async (title) => {
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
