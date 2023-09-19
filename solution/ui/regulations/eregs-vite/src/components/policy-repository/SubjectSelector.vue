<script setup>
import { computed, ref } from "vue";
import {
    getPolicyDocSubjects,
} from "utilities/api";

const props = defineProps({
    prop1: {
        type: String,
        required: true,
    },
    prop2: {
        type: Object,
        required: true,
    },
});

const policyDocSubjects = ref({
    results: [],
    loading: true,
});

const getDocSubjects = async () => {
    try {
        policyDocSubjects.value.results = await getPolicyDocSubjects({
            apiUrl: props.apiUrl,
        });
    } catch (error) {
        console.error(error);
    } finally {
        policyDocSubjects.value.loading = false;
    }
};

getDocSubjects();
</script>

<template>
    <div class="subjects__select-container">
        <select class="ds-c-field subjects__select">
            <option value="">- Select a subject -</option>
            <option
                v-for="subject in policyDocSubjects.results"
                :key="subject.id"
                :value="subject.id"
            >
                {{ subject.full_name }}
            </option>
        </select>
    </div>
</template>

<style></style>

