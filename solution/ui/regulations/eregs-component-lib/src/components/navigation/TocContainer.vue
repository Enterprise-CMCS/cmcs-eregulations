<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";

import { getTitles, getTOC } from "utilities/api";

const props = defineProps({
    apiUrl: {
        type: String,
        default: undefined,
    },
})

const getTitlesArray = async() => {
    const x = await getTitles(props.apiUrl);
    console.log("titles", x);
}

const getTableOfContents = async() => {
    const x = await getTOC({title: 42, apiUrl: props.apiUrl});
    console.log("42 toc", x);
}

getTitlesArray();
getTableOfContents();

</script>

<template>
    {{ props.structure }}
</template>

<style></style>
