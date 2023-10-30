<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router/composables";

import _isArray from "lodash/isArray";
import _isEmpty from "lodash/isEmpty";
import _isUndefined from "lodash/isUndefined";

import { DOCUMENT_TYPES, DOCUMENT_TYPES_MAP } from "utilities/utils";

const $route = useRoute();
const $router = useRouter();

const { type: typeParams } = $route.query;

// v-model to control if the checkbox displays as checked or not
const checkedBoxes = ref(
    _isUndefined(typeParams)
        ? [...DOCUMENT_TYPES]
        : _isArray(typeParams)
        ? typeParams
        : [typeParams]
);

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
        name: "policy-repository",
        query: queryClone,
    });
};

watch(
    () => $route.query,
    async (newQueryParams, oldQueryParams) => {
        const { type: newTypeParams } = newQueryParams;

        // "all" is only set when clicking a subject chip, so it is safe to use here
        if (!_isUndefined(newTypeParams) && newTypeParams.includes("all")) {
            checkedBoxes.value = [...DOCUMENT_TYPES];
        }
    }
);

// popstate to update the checkbox on back/forward click
const onPopState = () => {
    const { type: queryTypes } = $route.query;

    if (_isUndefined(queryTypes) || queryTypes === "all") {
        checkedBoxes.value = [...DOCUMENT_TYPES];
    } else if (_isArray(queryTypes)) {
        checkedBoxes.value = queryTypes;
    } else {
        checkedBoxes.value = [queryTypes];
    }
};

onMounted(() => {
    window.addEventListener("popstate", onPopState);
});
onUnmounted(() => window.removeEventListener("resize", onPopState));
</script>

<template>
    <div class="doc-type__toggle-container">
        <h3>Documents to Show</h3>
        <div class="doc-type__toggle">
            <fieldset class="ds-c-fieldset" aria-invalid="false">
                <div v-for="(type, index) in DOCUMENT_TYPES" :key="type">
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
                            <span class="">{{ DOCUMENT_TYPES_MAP[type] }}</span>
                        </label>
                    </div>
                </div>
            </fieldset>
        </div>
    </div>
</template>
