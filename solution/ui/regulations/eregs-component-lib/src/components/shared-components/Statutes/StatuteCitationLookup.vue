<script setup>
import { inject, ref } from "vue";

import useStatuteCitationLink from "composables/statuteCitationLink";

const citation = ref("");

const apiUrl = inject("apiUrl");

const { statuteCitationInfo, getStatuteCitationInfo } =
    useStatuteCitationLink();

const lookupCitation = async () => {
    getStatuteCitationInfo({
        apiUrl,
        citation: citation.value,
    });
};
</script>

<template>
    <form class="statute-citation-lookup__form" @submit.prevent="lookupCitation">
        <label for="citation-input">Social Security Act §</label>
        <input
            id="citationInput"
            v-model="citation"
            class="ds-c-field"
            type="text"
            placeholder="1903(a)(3)(A)(i)"
        >
        <button type="submit" class="action-btn default-btn">
            Get Citation Link
        </button>
    </form>
    <div v-if="statuteCitationInfo.loading">
        <p>Loading...</p>
    </div>
    <div v-if="statuteCitationInfo.error">
        <p>Error: {{ statuteCitationInfo.error }}</p>
    </div>
    <div v-if="statuteCitationInfo.results">
        <p>Text: {{ statuteCitationInfo.results }}</p>
    </div>
</template>

<style scoped>
    .statute-citation-lookup__form {
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    label {
        margin-right: 0.5rem;
        font-weight: bold;
    }
</style>
