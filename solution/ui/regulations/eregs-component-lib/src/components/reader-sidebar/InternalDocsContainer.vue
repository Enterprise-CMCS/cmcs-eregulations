<script setup>
import { computed, ref, watch } from "vue";

import { getPolicyDocCategories } from "utilities/api";

import SimpleSpinner from "../SimpleSpinner.vue";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
    part: {
        type: String,
        required: true,
    },
});

// What do I want to do?
// 1. Get the data from the API (categories and documents based on the section or subpart)
// 2. Display the data in a tree structure using existing components

const getCategories = async () => {
    const categories = await getPolicyDocCategories({
        apiUrl: props.apiUrl,
        cacheResponse: false,
    });
    console.log(categories);
};

getCategories();
</script>

<template>
    <div class="internal-docs__container">
        <SimpleSpinner />
    </div>
</template>

<style></style>
