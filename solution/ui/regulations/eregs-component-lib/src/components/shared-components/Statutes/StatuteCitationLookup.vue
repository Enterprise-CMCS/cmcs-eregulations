<script setup>
import { ref } from "vue";

const citation = ref("");

const emit = defineEmits(["lookup-citation"]);

const lookupCitation = () => {
    emit("lookup-citation", citation.value);
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
