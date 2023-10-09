<script setup>
import { inject, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router/composables";

import _isArray from "lodash/isArray";

const $router = useRouter();
const $route = useRoute();

const selectedParams = inject("selectedParams");
const FilterTypesDict = inject("FilterTypesDict");

const removeClick = (event) => {
    const subjects = _isArray($route.query.subjects)
        ? $route.query.subjects[0]
        : $route.query.subjects;

    const subjectIds = subjects
        ? subjects.split(",")
        : [];

    const filteredSubjects = subjectIds.filter(
        (subject) => subject !== event.target.dataset.id
    );

    const query = filteredSubjects.length
        ? {
              subjects: filteredSubjects.join(","),
          }
        : {};

    $router.push({
        name: "policy-repository",
        query,
    });
};

const selections = ref([]);

watch(
    () => selectedParams.paramString,
    async () => {
        selections.value = selectedParams.paramsArray
            .map((param) => ({
                label: FilterTypesDict[param.type],
                id: param.id,
                name: param.name,
            }))
            .sort((a, b) => {
                // sort by label and then by name
                if (a.label < b.label) return -1;
                if (a.label > b.label) return 1;
                if (a.name < b.name) return -1;
                if (a.name > b.name) return 1;
                return 0;
            });
    }
);
</script>

<template>
    <div class="selections__container">
        <ul v-if="selections.length > 0" class="selections__list">
            <li
                v-for="selection in selections"
                :key="selection.id"
                class="selections__li"
            >
                {{ selection.label }}: {{ selection.name }}
                <button
                    :data-id="selection.id"
                    :data-testid="`remove-subject-${selection.id}`"
                    @click="removeClick"
                >
                    <i class="mdi mdi-close"></i>
                </button>
            </li>
        </ul>
    </div>
</template>
