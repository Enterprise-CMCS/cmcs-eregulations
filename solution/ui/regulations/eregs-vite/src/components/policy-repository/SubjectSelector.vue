<script setup>
import { computed, ref } from "vue";
import { getPolicyDocSubjects } from "utilities/api";

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

const subjectClick = (event) => {
    console.log("event", event.currentTarget);
};

const selectedSubject = ref();

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
        <h3>By Subject Matter</h3>
        <ul tabindex="-1" class="subjects__list">
            <li
                v-for="subject in policyDocSubjects.results"
                :key="subject.id"
                class="subjects__li sidebar__li"
            >
                <button
                    :data-full-name="subject.full_name"
                    :data-id="subject.id"
                    :title="subject.full_name"
                    @click="subjectClick"
                >
                    {{
                        subject.short_name ||
                        subject.abbreviation ||
                        subject.full_name
                    }}
                </button>
            </li>
        </ul>
    </div>
</template>

<style></style>
