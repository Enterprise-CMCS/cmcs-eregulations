<script setup>
import { ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router/composables";

import _isArray from "lodash/isArray";
import _isEmpty from "lodash/isEmpty";
import _isUndefined from "lodash/isUndefined";

import { DOCUMENT_TYPES } from "utilities/utils";

const $route = useRoute();
const $router = useRouter();

const typeParams = $route.query?.type;
const typesArray = _isUndefined(typeParams)
    ? [...DOCUMENT_TYPES]
    : _isArray(typeParams)
    ? typeParams
    : [typeParams];

const typesRef = ref(typesArray);

watch(typesRef, (newVal) => {
    const routeClone = { ...$route.query };

    if (_isEmpty(newVal)) {
        delete routeClone.type;
    } else {
        routeClone.type = newVal;
    }

    $router.push({
        name: "policy-repository",
        query: {
            ...routeClone
        },
    });
});
</script>

<template>
    <div class="doc-type__toggle-container">
        <h3>Documents to Show</h3>
        <div class="doc-type__toggle">
            <fieldset class="ds-c-fieldset" aria-invalid="false">
                <div>
                    <div class="ds-c-choice-wrapper">
                        <input
                            id="choice-list--1__choice--0"
                            v-model="typesRef"
                            class="ds-c-choice ds-c-choice--small"
                            name="checkbox_choices"
                            type="checkbox"
                            value="external"
                        /><label class="ds-c-label" for="choice-list--1__choice--0"
                            ><span class="">Formal Guidance</span></label
                        >
                    </div>
                </div>
                <div>
                    <div class="ds-c-choice-wrapper">
                        <input
                            id="choice-list--1__choice--1"
                            v-model="typesRef"
                            class="ds-c-choice ds-c-choice--small"
                            name="checkbox_choices"
                            type="checkbox"
                            value="internal"
                        /><label class="ds-c-label" for="choice-list--1__choice--1"
                            ><span class="">Informal Guidance</span
                        >
                    </div>
                </div>
            </fieldset>
        </div>
    </div>
</template>
