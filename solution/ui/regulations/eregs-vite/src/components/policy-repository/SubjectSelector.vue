<script setup>
import { computed, reactive, watch } from "vue";

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
    if (!filter || filter.length < 1) {
        state.subjects = props.policyDocSubjects.results;
        return;
    }

    state.subjects = props.policyDocSubjects.results.reduce((acc, subject) => {
        const shortNameMatch = subject.short_name
            ? subject.short_name.toLowerCase().includes(filter.toLowerCase())
            : false;
        const abbreviationMatch = subject.abbreviation
            ? subject.abbreviation.toLowerCase().includes(filter.toLowerCase())
            : false;
        const fullNameMatch = subject.full_name
            ? subject.full_name.toLowerCase().includes(filter.toLowerCase())
            : false;

        if (shortNameMatch || abbreviationMatch || fullNameMatch) {
            const newSubject = {
                ...subject,
                title: subject.full_name,
                short_name: shortNameMatch
                    ? "<span class='match__container'>" +
                      subject.short_name.replace(
                          new RegExp(filter, "gi"),
                          (match) => `<span class="match">${match}</span>`
                      ) +
                      "</span>"
                    : subject.short_name,
                abbreviation: abbreviationMatch
                    ? "<span class='match__container'>" +
                      subject.abbreviation.replace(
                          new RegExp(filter, "gi"),
                          (match) => `<span class="match">${match}</span>`
                      ) +
                      "</span>"
                    : subject.abbreviation,
                full_name: fullNameMatch
                    ? "<span class='match__container'>" +
                      subject.full_name.replace(
                          new RegExp(filter, "gi"),
                          (match) => `<span class="match">${match}</span>`
                      ) +
                      "</span>"
                    : subject.full_name,
            };
            return [...acc, newSubject];
        }

        return acc;
    }, []);
};

const debouncedFilter = _debounce(getFilteredSubjects, 100);

watch(() => state.filter, debouncedFilter);

const subjectClick = (event) => {
    const subjects = $route?.query?.subjects ?? [];
    const subjectsArray = _isArray(subjects) ? subjects : [subjects];
    const subjectToAdd = event.currentTarget.dataset.id;

    if (subjectsArray.includes(subjectToAdd)) return;

    $router.push({
        name: "policy-repository",
        query: {
            ...$route.query,
            subjects: [...subjectsArray, event.currentTarget.dataset.id],
        },
    });
};

const filterResetClasses = computed(() => ({
    "subjects__filter-reset": true,
    "subjects__filter-reset--hidden": !state.filter,
}));

const filterResetClick = () => {
    state.filter = "";
};
</script>

<template>
    <div class="subjects__select-container">
        <h3>By Subject</h3>
        <div class="subjects__list-container">
            <form>
                <label for="subjectReduce">Filter the subject list</label>
                <input id="subjectReduce" v-model="state.filter" type="text" />
                <button
                    aria-label="Clear subject list filter"
                    data-testid="clear-subject-filter"
                    type="reset"
                    :class="filterResetClasses"
                    class="mdi mdi-close"
                    @click="filterResetClick"
                ></button>
            </form>
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
                        :title="subject.title || subject.full_name"
                        @click="subjectClick"
                        v-html="getSubjectName(subject)"
                    ></button>
                </li>
            </ul>
        </div>
    </div>
</template>
