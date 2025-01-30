<script>
const getUnselectedSubjects = ({
    parent = "subjects",
    subjectsList,
    subjectId,
}) => {
    if (parent === "search") return subjectsList;

    return subjectsList.filter(
        (subject) => subjectId !== subject.id.toString()
    );
};

const getInputContainerClasses = ({ parent }) => ({
    "subjects__input--sidebar": parent === "subjects",
});

const getListItemClasses = ({ parent }) => ({
    sidebar__li: parent === "subjects",
});

const getSubjectClasses = ({ subjectId, subjectQueryParam }) => {
    const routeArr = _isArray(subjectQueryParam)
        ? subjectQueryParam
        : [subjectQueryParam];

    return {
        "subjects-li__button": true,
        "subjects-li__button--selected": routeArr.includes(
            subjectId.toString()
        ),
    };
};

const getFilterResetClasses = ({ filter }) => ({
    "subjects__filter-reset": true,
    "subjects__filter-reset--hidden": !filter,
});

export default {
    getInputContainerClasses,
    getListItemClasses,
    getSubjectClasses,
    getFilterResetClasses,
    getUnselectedSubjects,
};
</script>

<script setup>
import { computed, inject, reactive, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

import useRemoveList from "composables/removeList";

import _debounce from "lodash/debounce";
import _isArray from "lodash/isArray";

import { getSubjectName } from "utilities/filters";

import SelectedSubjectChip from "./SelectedSubjectChip.vue";
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
    placeholder: {
        type: String,
        default: "Find a subject",
    },
});

const $router = useRouter();
const $route = useRoute();

const removeList = inject("commonRemoveList", []);
const parent = inject("parent", "subjects");

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

        if ($route.query.subjects) {
            state.subjects = getUnselectedSubjects({
                parent,
                subjectsList: props.policyDocSubjects.results,
                subjectId: $route.query.subjects,
            });
        } else {
            state.subjects = props.policyDocSubjects.results;
        }
    }
);

watch(
    () => $route.query.subjects,
    () => {
        state.subjects = getUnselectedSubjects({
            parent,
            subjectsList: props.policyDocSubjects.results,
            subjectId: $route.query.subjects,
        });
    }
);

const getFilteredSubjects = (filter) => {
    if (!filter || filter.length < 1) {
        state.subjects = getUnselectedSubjects({
            parent,
            subjectsList: props.policyDocSubjects.results,
            subjectId: $route.query.subjects,
        });
        return;
    }

    state.subjects = props.policyDocSubjects.results
        .filter((subject) => $route.query.subjects !== subject.id.toString())
        .reduce((acc, subject) => {
            const shortNameMatch = subject.short_name
                ? subject.short_name
                      .toLowerCase()
                      .includes(filter.toLowerCase())
                : false;
            const abbreviationMatch = subject.abbreviation
                ? subject.abbreviation
                      .toLowerCase()
                      .includes(filter.toLowerCase())
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
    state.filter = "";

    const routeClone = { ...$route.query };

    const subjects = routeClone?.subjects ?? [];
    const subjectsArray = _isArray(subjects) ? subjects : [subjects];
    const subjectToAdd = event.currentTarget.dataset.id;

    if (subjectsArray.includes(subjectToAdd)) return;

    let filteredTypes;

    if (parent === "search") {
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
        name: parent,
        query: {
            ...cleanedRoute,
            subjects: subjectToAdd,
            type: filteredTypes,
        },
    });
};

const inputContainerClasses = computed(() =>
    getInputContainerClasses({ parent })
);

const listItemClasses = computed(() => getListItemClasses({ parent }));

const filterResetClasses = computed(() =>
    getFilterResetClasses({ filter: state.filter })
);

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
                        >
                        <button
                            aria-label="Clear subject list filter"
                            data-testid="clear-subject-filter"
                            type="reset"
                            :class="filterResetClasses"
                            class="mdi mdi-close"
                            @keydown.enter="filterResetClick"
                            @click="filterResetClick"
                        />
                    </form>
                    <slot
                        name="selection"
                        :selected-subject="
                            props.policyDocSubjects.results.find(
                                (subject) =>
                                    $route.query.subjects ===
                                    subject.id.toString()
                            )
                        "
                    />
                </div>
                <ul tabindex="-1" class="subjects__list">
                    <li
                        v-for="subject in state.subjects"
                        :key="subject.id"
                        class="subjects__li"
                        :class="listItemClasses"
                    >
                        <button
                            :class="
                                getSubjectClasses({
                                    subjectId: subject.id,
                                    subjectQueryParam: $route.query.subjects,
                                })
                            "
                            :data-name="getSubjectName(subject)"
                            :data-id="subject.id"
                            :data-testid="`add-subject-${subject.id}`"
                            :title="subject.full_name"
                            @keydown.enter="subjectClick"
                            @keydown.up.prevent="liUpArrowPress"
                            @keydown.down.prevent="liDownArrowPress"
                            @click="subjectClick"
                        >
                            <SelectedSubjectChip :subject="subject" />
                        </button>
                    </li>
                </ul>
            </template>
        </div>
    </div>
</template>
