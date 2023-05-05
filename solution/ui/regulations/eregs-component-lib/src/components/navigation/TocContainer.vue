<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import { getTitles, getTOC } from "utilities/api";

const props = defineProps({
    apiUrl: {
        type: String,
        default: undefined,
    },
});

const titles = ref([]);
const getTitlesArray = async () => {
    const titlesArray = await getTitles(props.apiUrl);
    titles.value = titlesArray;
};

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
    getTOCs(newVal)
});

getTitlesArray();
</script>

<template>
    <div>{{ titles }}</div>
</template>

<style></style>
