<script setup>
import { ref, inject, onMounted, onUnmounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

import _isArray from "lodash/isArray";
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

if (!isAuthenticated) {
    docTypesArr = docTypesArr.filter((type) => type !== "internal");
}

// v-model with a ref to control if the checkbox is displayed as checked or not
let boxesArr;

if (_isUndefined(typeParams) || typeParams.includes("all")) {
    boxesArr = [];
} else if (_isArray(typeParams)) {
    boxesArr = typeParams;
} else {
    boxesArr = [typeParams];
}

const checkedBoxes = ref(boxesArr);

// onClick event to set the $route
const toggleDocumentType = (clickedType) => {
    const { type: queryCloneType, ...queryClone } = $route.query;
    const refTypesBeforeClick = checkedBoxes.value;

    if (_isEmpty(refTypesBeforeClick)) {
        queryClone.type = [clickedType];
    } else if (refTypesBeforeClick.includes(clickedType)) {
        const filteredTypes = refTypesBeforeClick.filter(
            (docType) => docType !== clickedType
        );
        if (!_isEmpty(filteredTypes)) {
            queryClone.type = filteredTypes;
        }
    }

    $router.push({
        name: props.parent,
        query: {
            ...queryClone,
            page: undefined,
        },
    });
};

watch(
    () => $route.query,
    async (newQueryParams) => {
        if (!isAuthenticated) {
            return;
        }

        const { type: newTypeParams } = newQueryParams;

        if (!_isUndefined(newTypeParams)) {
            if (newTypeParams.includes("all")) {
                checkedBoxes.value = [];
                return;
            }

            if (_isArray(newTypeParams)) {
                checkedBoxes.value = newTypeParams;
            } else {
                checkedBoxes.value = [newTypeParams];
            }
        }
    }
);

// popstate to update the checkbox on back/forward click
const onPopState = (event) => {
    if (!isAuthenticated) {
        return;
    }

    const currentPopState = event?.state?.current ?? "";

    const isInternal =
        currentPopState.includes("type") &&
        currentPopState.includes("internal");
    const isExternal =
        currentPopState.includes("type") &&
        currentPopState.includes("external");
    const isAll =
        currentPopState.includes("type") && currentPopState.includes("all");
    const isNone = !currentPopState.includes("type");

    if (isInternal) {
        checkedBoxes.value = ["internal"];
    } else if (isExternal) {
        checkedBoxes.value = ["external"];
    } else if (isAll || isNone) {
        checkedBoxes.value = [];
    }
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
                            @click="toggleDocumentType(type)"
                        />
                        <label
                            class="ds-c-label"
                            :for="`choice-list--1__choice--${index}`"
                        >
                            <span class=""
                                >{{ DOCUMENT_TYPES_MAP[type] }} Resources</span
                            >
                        </label>
                    </div>
                </div>
            </fieldset>
        </div>
    </div>
</template>
