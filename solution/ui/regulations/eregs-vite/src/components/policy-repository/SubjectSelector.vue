<script setup>
import { reactive, watch } from "vue";

import { useRouter, useRoute } from "vue-router/composables";

import _debounce from "lodash/debounce";
import _isArray from "lodash/isArray";

import { getSubjectName } from "utilities/filters";

const props = defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
});

const $router = useRouter();
const $route = useRoute();

const state = reactive({
    filter: "",
    subjects: [],
});

watch(
    () => props.policyDocSubjects.loading,
    (loading) => {
        if (loading) {
            state.subjects = [];
            return;
        }

        state.subjects = props.policyDocSubjects.results;
    }
);

const getFilteredSubjects = (filter) => {
    if (!filter || filter.length < 3) {
        state.subjects = props.policyDocSubjects.results;
        return;
    }

    state.subjects = props.policyDocSubjects.results.filter((subject) => {
        const shortNameMatch = subject.short_name
            ? subject.short_name.toLowerCase().includes(filter.toLowerCase())
            : false;
        const abbreviationMatch = subject.abbreviation
            ? subject.abbreviation.toLowerCase().includes(filter.toLowerCase())
            : false;
        const fullNameMatch = subject.full_name
            ? subject.full_name.toLowerCase().includes(filter.toLowerCase())
            : false;

        return shortNameMatch || abbreviationMatch || fullNameMatch;
    });
};

const debouncedFilter = _debounce(getFilteredSubjects, 100);

watch(() => state.filter, debouncedFilter);

const subjectClick = (event) => {
    const subjects = $route?.query?.subjects ?? [];
    const subjectsArray = _isArray(subjects) ? subjects : [subjects];
    const subjectToAdd = event.target.dataset.id;

    if (subjectsArray.includes(subjectToAdd)) return;

    $router.push({
        name: "policy-repository",
        query: {
            ...$route.query,
            subjects: [...subjectsArray, event.target.dataset.id],
        },
    });
};
</script>

<template>
    <div class="subjects__select-container">
        <h3>By Subject</h3>
        <div class="subjects__list-container">
            <label for="subjectReduce">Filter the subject list</label>
            <input id="subjectReduce" v-model="state.filter" type="text" />
            <ul tabindex="-1" class="subjects__list">
                <li
                    v-for="subject in state.subjects"
                    :key="subject.id"
                    class="subjects__li sidebar__li"
                >
                    <button
                        :data-name="getSubjectName(subject)"
                        :data-id="subject.id"
                        :data-testid="`add-subject-${subject.id}`"
                        :title="subject.full_name"
                        @click="subjectClick"
                    >
                        {{ getSubjectName(subject) }}
                    </button>
                </li>
            </ul>
        </div>
    </div>
</template>
