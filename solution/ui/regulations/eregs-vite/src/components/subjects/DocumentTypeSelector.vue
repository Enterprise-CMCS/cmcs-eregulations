<script setup>
import { ref, inject, onMounted, onUnmounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

import useCounts from "composables/counts";

import _isArray from "lodash/isArray";
import _intersection from "lodash/intersection";
import _isEmpty from "lodash/isEmpty";
import _isUndefined from "lodash/isUndefined";

import {
    COUNT_TYPES_MAP,
    DOCUMENT_TYPES,
    DOCUMENT_TYPES_MAP,
} from "utilities/utils";

const props = defineProps({
    parent: {
        type: String,
        default: "subjects",
    },
    loading: {
        type: Boolean,
        default: false,
    },
});

const $route = useRoute();
const $router = useRouter();

const { type: typeParams } = $route.query;

const apiUrl = inject("apiUrl");
const isAuthenticated = inject("isAuthenticated");

let docTypesArr = DOCUMENT_TYPES;

if (props.parent !== "search")
    docTypesArr = docTypesArr.filter((type) => type !== "regulations");

if (!isAuthenticated)
    docTypesArr = docTypesArr.filter((type) => type !== "internal");

const { counts, fetchCounts } = useCounts();

fetchCounts({ apiUrl, queryParams: $route.query });

// v-model with a ref to control if the checkbox is displayed as checked or not
let boxesArr;

if (_isUndefined(typeParams) || typeParams.includes("all")) {
    boxesArr = [];
} else {
    boxesArr = typeParams.split(",");
}

const checkedBoxes = ref(boxesArr);

const onCheckboxChange = (event) => {
    const { checked, value } = event.target;
    const { type, ...queryClone } = $route.query;

    if (checked) {
        checkedBoxes.value = [...checkedBoxes.value, value];
    } else {
        checkedBoxes.value = checkedBoxes.value.filter(
            (item) => item !== value
        );
    }

    // if only Regulations is checked, remove categories from route
    if (
        checkedBoxes.value.length === 1 &&
        checkedBoxes.value[0] === "regulations"
    ) {
        $router.push({
            name: props.parent,
            query: {
                ...queryClone,
                type: "regulations",
                categories: undefined,
                page: undefined,
            },
        });

        return;
    }

    const newTypes = _isEmpty(checkedBoxes.value)
        ? undefined
        : checkedBoxes.value.join(",");

    $router.push({
        name: props.parent,
        query: {
            ...queryClone,
            type: newTypes,
            page: undefined,
        },
    });
};

watch(
    () => $route.query,
    (newQuery) => {
        const { type: typeParams } = newQuery;

        fetchCounts({ apiUrl, queryParams: newQuery });

        if (_isUndefined(typeParams) || typeParams.includes("all")) {
            checkedBoxes.value = [];
        } else {
            checkedBoxes.value = typeParams.split(",");
        }
    }
);

const onPopState = (event) => {
    const currentPopState = event?.state?.current ?? "";
    const currentPopStateArr = currentPopState.split("?");

    if (currentPopStateArr.length > 1) {
        const queryParams = new URLSearchParams(currentPopStateArr[1]);
        const type = queryParams.get("type");

        checkedBoxes.value = type ? type.split(",") : [];
    }
};

const makeLabel = ({ type }) => {
    return `${DOCUMENT_TYPES_MAP[type]}${
        type !== "regulations" ? " Resources" : ""
    }`;
};

const makeCount = ({ type }) => {
    if (props.loading) return "";

    const mappedType = COUNT_TYPES_MAP[type];

    return _isUndefined(counts.value.results[mappedType])
        ? ""
        : `(${counts.value.results[mappedType]})`;
};

onMounted(() => {
    window.addEventListener("popstate", onPopState);
});
onUnmounted(() => {
    window.removeEventListener("popstate", onPopState);
});
</script>

<template>
    <div class="doc-type__toggle-container">
        <div class="doc-type__toggle">
            <fieldset class="ds-c-fieldset" aria-invalid="false">
                <template v-if="showRegulations"> </template>
                <div v-for="(type, index) in docTypesArr" :key="type">
                    <div class="ds-c-choice-wrapper">
                        <input
                            :id="`choice-list--1__choice--${index}`"
                            class="ds-c-choice ds-c-choice--small"
                            name="checkbox_choices"
                            type="checkbox"
                            :value="type"
                            :checked="checkedBoxes.includes(type)"
                            :disabled="loading"
                            @change="onCheckboxChange"
                        />
                        <label
                            class="ds-c-label"
                            :for="`choice-list--1__choice--${index}`"
                        >
                            <span class="label__span">{{
                                makeLabel({ type })
                            }}</span>
                            <span class="count__span">{{
                                makeCount({ type })
                            }}</span>
                        </label>
                    </div>
                </div>
            </fieldset>
        </div>
    </div>
</template>
