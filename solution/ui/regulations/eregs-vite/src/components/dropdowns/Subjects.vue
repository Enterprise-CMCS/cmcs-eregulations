<script setup>
import { computed, ref } from "vue";

import { getSubjectName } from "utilities/filters";

import SubjectSelector from "@/components/subjects/SubjectSelector.vue";

const props = defineProps({
    list: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <v-btn id="subjects-activator" variant="outlined" density="compact" flat
        ><span>Test</span></v-btn
    >
    <v-menu activator="#subjects-activator">
        <SubjectSelector
            :policy-doc-subjects="list"
            class="subjects__select-container--menu"
            component-type="dropdown"
            parent="search"
        />
    </v-menu>
</template>

<style></style>
