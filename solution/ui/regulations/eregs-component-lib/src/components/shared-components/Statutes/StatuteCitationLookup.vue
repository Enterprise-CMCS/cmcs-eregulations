<script setup>
import { computed, inject, ref } from "vue";

import StatuteCitationTable from "eregsComponentLib/src/components/shared-components/Statutes/StatuteCitationTable.vue";

import useStatuteCitationLink from "composables/statuteCitationLink";

const citation = ref("");

const apiUrl = inject("apiUrl");

const { statuteCitationInfo, getStatuteCitationInfo, clearStatuteCitationInfo } =
    useStatuteCitationLink();

const lookupCitation = async () => {
    getStatuteCitationInfo({
        apiUrl,
        citation: citation.value,
    });
};

const clearCitationClick = (event) => {
    event.stopPropagation();
    clearStatuteCitationInfo();
    citation.value = "";
};

const getCitationClearClasses = ({ filter }) => ({
    "citation-reset__button": true,
    "citation-reset__button--hidden": !filter,
});

const citationClearClasses = computed(() =>
    getCitationClearClasses({ filter: citation.value })
);

</script>

<template>
    <form class="statute-citation-lookup__form" @submit.prevent="lookupCitation">
        <label
            class="statute-citation-lookup__form--label"
            for="citationInput"
        >Social Security Act §</label>
        <div class="statute-citation-lookup__form--input-group">
            <input
                id="citationInput"
                v-model="citation"
                class="ds-c-field"
                type="text"
                placeholder="1903(a)(3)(A)(i)"
                required
            >
            <button
                aria-label="Clear citation input"
                data-testid="clear-citation-input"
                type="reset"
                :class="citationClearClasses"
                class="mdi mdi-close"
                @keydown.enter="clearCitationClick"
                @click="clearCitationClick"
            />
        </div>
        <button
            id="citationSubmit"
            type="submit"
            class="action-btn default-btn"
        >
            Get Citation Link
        </button>
    </form>
    <div v-if="statuteCitationInfo.loading">
        <p>Loading...</p>
    </div>
    <StatuteCitationTable
        v-if="!statuteCitationInfo.loading"
        :citation-obj="statuteCitationInfo.results"
        :error="statuteCitationInfo.error"
    />
</template>
