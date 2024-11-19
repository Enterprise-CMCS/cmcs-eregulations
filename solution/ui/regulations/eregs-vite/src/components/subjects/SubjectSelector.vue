<script>
const getDisplayCount = (subject) => {
    return subject.count ? `<span class="count">(${subject.count})</span>` : "";
};

export default {
    getDisplayCount,
};
</script>

<script setup>
import { computed, inject, reactive, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

import useRemoveList from "composables/removeList";

import _debounce from "lodash/debounce";
import _isArray from "lodash/isArray";

import { getSubjectName, getSubjectNameParts } from "utilities/filters";

import SimpleSpinner from "eregsComponentLib/src/components/SimpleSpinner.vue";

const props = defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
    componentType: {
        type: String,
        default: "default",
    },
    parent: {
        type: String,
        default: "subjects",
    },
    placeholder: {
        type: String,
        default: "Find a subject",
    },
});

const $router = useRouter();
const $route = useRoute();

const removeList = inject("commonRemoveList", []);

const state = reactive({
    filter: "",
    subjects: [],
});

if (!props.policyDocSubjects.loading) {
    state.subjects = props.policyDocSubjects.results;
}

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
            let displayName;

            if (shortNameMatch) {
                displayName = subject.short_name;
            } else if (abbreviationMatch) {
                displayName = subject.abbreviation;
            } else if (fullNameMatch) {
                displayName = subject.full_name;
            }

            displayName =
                "<span class='match__container'>" +
                displayName.replace(
                    new RegExp(filter, "gi"),
                    (match) => `<span class="match">${match}</span>`
                ) +
                "</span>";

            const newSubject = {
                ...subject,
                displayName,
            };

            return [...acc, newSubject];
        }

        return acc;
    }, []);
};

const debouncedFilter = _debounce(getFilteredSubjects, 100);

watch(() => state.filter, debouncedFilter);

const subjectClick = (event) => {
    const routeClone = { ...$route.query };

    const subjects = routeClone?.subjects ?? [];
    const subjectsArray = _isArray(subjects) ? subjects : [subjects];
    const subjectToAdd = event.currentTarget.dataset.id;

    if (subjectsArray.includes(subjectToAdd)) return;

    let filteredTypes;

    if (props.parent === "search") {
        const type = routeClone?.type;
        const typesArr = type ? type.split(",") : [];

        const filteredTypesArr = typesArr.filter(
            (item) => item !== "regulations"
        );

        filteredTypes =
            filteredTypesArr.length > 0
                ? filteredTypesArr.join(",")
                : undefined;
    }

    const cleanedRoute = useRemoveList({
        route: routeClone,
        removeList,
    });

    $router.push({
        name: props.parent,
        query: {
            ...cleanedRoute,
            subjects: subjectToAdd,
            type: filteredTypes,
        },
    });
};

const inputContainerClasses = computed(() => ({
    "subjects__input--sidebar": props.parent === "subjects",
}));

const listItemClasses = computed(() => ({
    sidebar__li: props.parent === "subjects",
}));

const buttonTextClasses = computed(() => ({
    "subjects-li__button-text--sidebar": props.parent === "subjects",
}));

const subjectClasses = (subjectId) => {
    const routeArr = _isArray($route.query.subjects)
        ? $route.query.subjects
        : [$route.query.subjects];

    return {
        "subjects-li__button": true,
        "subjects-li__button--selected": routeArr.includes(
            subjectId.toString()
        ),
    };
};

const filterResetClasses = computed(() => ({
    "subjects__filter-reset": true,
    "subjects__filter-reset--hidden": !state.filter,
}));

const filterResetClick = (event) => {
    event.stopPropagation();
    state.filter = "";
};

const inputUpArrowPress = (event) => {
    if (event.key === "ArrowUp") {
        const lastSubject = document.querySelector(
            ".subjects__li:last-child button"
        );

        if (lastSubject) {
            lastSubject.focus();
        }
    }
};

const inputDownArrowPress = (event) => {
    if (event.key === "ArrowDown") {
        const firstSubject = document.querySelector(".subjects__li");

        if (firstSubject) {
            firstSubject.querySelector("button").focus();
        }
    }
};

const liUpArrowPress = (event) => {
    if (event.key === "ArrowUp") {
        const currentSubject = event.currentTarget;
        const previousSubject =
            currentSubject.parentNode.previousElementSibling;

        if (previousSubject) {
            previousSubject.querySelector("button").focus();
        } else {
            document.querySelector("input#subjectReduce").focus();
        }
    }
};

const liDownArrowPress = (event) => {
    if (event.key === "ArrowDown") {
        const currentSubject = event.currentTarget;
        const nextSubject = currentSubject.parentNode.nextElementSibling;

        if (nextSubject) {
            nextSubject.querySelector("button").focus();
        } else {
            document.querySelector("input#subjectReduce").focus();
        }
    }
};
</script>

<template>
    <div class="subjects__select-container">
        <div class="subjects__list-container">
            <template v-if="props.policyDocSubjects.loading">
                <div class="subjects__loading">
                    <SimpleSpinner />
                </div>
            </template>
            <template v-else>
                <div :class="inputContainerClasses">
                    <form @submit.prevent>
                        <input
                            id="subjectReduce"
                            v-model="state.filter"
                            :aria-label="placeholder"
                            :placeholder="placeholder"
                            type="text"
                            @keydown.up.prevent="inputUpArrowPress"
                            @keydown.down.prevent="inputDownArrowPress"
                        />
                        <button
                            aria-label="Clear subject list filter"
                            data-testid="clear-subject-filter"
                            type="reset"
                            :class="filterResetClasses"
                            class="mdi mdi-close"
                            @keydown.enter="filterResetClick"
                            @click="filterResetClick"
                        ></button>
                    </form>
                    <slot name="selection"></slot>
                </div>
                <ul tabindex="-1" class="subjects__list">
                    <li
                        v-for="subject in state.subjects"
                        :key="subject.id"
                        class="subjects__li"
                        :class="listItemClasses"
                    >
                        <button
                            :class="subjectClasses(subject.id)"
                            :data-name="getSubjectName(subject)"
                            :data-id="subject.id"
                            :data-testid="`add-subject-${subject.id}`"
                            :title="subject.full_name"
                            @keydown.enter="subjectClick"
                            @keydown.up.prevent="liUpArrowPress"
                            @keydown.down.prevent="liDownArrowPress"
                            @click="subjectClick"
                        >
                            <span
                                class="subjects-li__button-text"
                                :class="buttonTextClasses"
                                v-html="
                                    (subject.displayName ||
                                        getSubjectName(subject)) +
                                    getDisplayCount(subject)
                                "
                            ></span>
                            <span
                                v-if="
                                    parent === 'subjects' &&
                                    !subject.displayName &&
                                    getSubjectNameParts(subject)[0][1]
                                "
                                class="subjects-li__button-subtitle"
                            >
                                {{ getSubjectNameParts(subject)[1][0] }}
                            </span>
                        </button>
                    </li>
                </ul>
            </template>
        </div>
    </div>
</template>
