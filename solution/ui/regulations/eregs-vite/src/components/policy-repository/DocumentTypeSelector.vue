<script setup>
import { useRouter, useRoute } from "vue-router/composables";

import { getSubjectName } from "utilities/filters";

const props = defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
});

const $router = useRouter();
const $route = useRoute();

const subjectClick = (event) => {
    const subjects = $route.query.subjects ?? [];
    const subjectToAdd = event.target.dataset.id;

    if (subjects.includes(subjectToAdd)) return;

    $router.push({
        name: "policy-repository",
        query: {
            ...$route.query,
            subjects: [...subjects, event.target.dataset.id],
        },
    });
};
</script>

<template>
    <div class="doc-type__toggle-container">
        <h3>Documents to Show</h3>
        <div class="doc-type__toggle">
            <fieldset class="ds-c-fieldset" aria-invalid="false">
                <div>
                    <div class="ds-c-choice-wrapper">
                        <input
                            class="ds-c-choice ds-c-choice--small"
                            id="choice-list--1__choice--0"
                            name="checkbox_choices"
                            type="checkbox"
                            value="A"
                        /><label class="ds-c-label" for="choice-list--1__choice--0"
                            ><span class="">Formal Guidance</span></label
                        >
                    </div>
                </div>
                <div>
                    <div class="ds-c-choice-wrapper">
                        <input
                            class="ds-c-choice ds-c-choice--small"
                            id="choice-list--1__choice--1"
                            name="checkbox_choices"
                            type="checkbox"
                            value="B"
                        /><label class="ds-c-label" for="choice-list--1__choice--1"
                            ><span class="">Informal Guidance</span
                        >
                    </div>
                </div>
            </fieldset>
        </div>
    </div>
</template>
