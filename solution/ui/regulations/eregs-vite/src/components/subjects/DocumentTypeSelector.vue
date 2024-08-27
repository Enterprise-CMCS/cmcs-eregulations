<script setup>
import { ref, inject, onMounted, onUnmounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

import _isArray from "lodash/isArray";
import _intersection from "lodash/intersection";
import _isEmpty from "lodash/isEmpty";
import _isUndefined from "lodash/isUndefined";

import { DOCUMENT_TYPES, DOCUMENT_TYPES_MAP } from "utilities/utils";

const props = defineProps({
    parent: {
        type: String,
        default: "subjects",
    },
});

const $route = useRoute();
const $router = useRouter();

const { type: typeParams } = $route.query;

const isAuthenticated = inject("isAuthenticated");

let docTypesArr = DOCUMENT_TYPES;

if (props.parent !== "search")
    docTypesArr = docTypesArr.filter((type) => type !== "regulations");

if (!isAuthenticated)
    docTypesArr = docTypesArr.filter((type) => type !== "internal");

// v-model with a ref to control if the checkbox is displayed as checked or not
let boxesArr;

if (_isUndefined(typeParams) || typeParams.includes("all")) {
    boxesArr = [];
} else {
    boxesArr = typeParams.split(",");
}

const checkedBoxes = ref(boxesArr);

watch(
    () => checkedBoxes.value,
    (newCheckedBoxes) => {
        const { type, ...queryClone } = $route.query;

        const intersection = _intersection(newCheckedBoxes, docTypesArr);

        const newTypes = _isEmpty(intersection)
            ? undefined
            : intersection.join(",");

        $router.push({
            name: props.parent,
            query: {
                ...queryClone,
                type: newTypes,
                page: undefined,
            },
        });
    }
);

// popstate to update the checkbox on back/forward click
const onPopState = (event) => {
    const currentPopState = event?.state?.current ?? "";
    const currentPopStateArr = currentPopState.split("?");
    console.log("currentPopStateArr", currentPopStateArr);

    if (currentPopStateArr.length > 1) {
        const queryParams = new URLSearchParams(currentPopStateArr[1]);
        const type = queryParams.get("type");

        console.log("type", type);

        if (_isUndefined(type) || type.includes("all")) {
            checkedBoxes.value = [];
        } else {
            checkedBoxes.value = type.split(",");
        }
    } else {
        checkedBoxes.value = [];
    }

    // checkedBoxes.value = currentPopState;
};

onMounted(() => {
    window.addEventListener("popstate", onPopState);
});
onUnmounted(() => window.removeEventListener("resize", onPopState));
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
                            v-model="checkedBoxes"
                            class="ds-c-choice ds-c-choice--small"
                            name="checkbox_choices"
                            type="checkbox"
                            :value="type"
                        />
                        <label
                            class="ds-c-label"
                            :for="`choice-list--1__choice--${index}`"
                        >
                            <span class=""
                                >{{ DOCUMENT_TYPES_MAP[type]
                                }}<span v-if="type !== 'regulations'">
                                    Resources</span
                                ></span
                            >
                        </label>
                    </div>
                </div>
            </fieldset>
        </div>
    </div>
</template>
