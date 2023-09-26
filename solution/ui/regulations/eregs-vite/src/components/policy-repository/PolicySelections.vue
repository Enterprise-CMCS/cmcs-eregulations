<script setup>
import { inject, ref, watch } from "vue";

import { useRouter, useRoute } from "vue-router/composables";

const $router = useRouter();
const $route = useRoute();

const FilterTypesEnum = {
    subjects: "Subject",
};

const selectedParams = inject("selectedParams");

const removeClick = (event) => {
    const subjects = $route.query.subjects
        ? $route.query.subjects.split(",")
        : [];

    const filteredSubjects = subjects.filter(
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

const selections = ref({});

watch(
    () => selectedParams.paramString,
    async () => {
        selections.value = selectedParams.paramsArray
            .map((param) => ({
                label: FilterTypesEnum[param.type],
                id: param.id,
                name: param.name,
            }))
            .sort((a, b) => {
                // sort by label and then by id
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
        <ul>
            <li v-for="selection in selections" :key="selection.id">
                {{ selection.label }}: {{ selection.name }} {{ selection.id }}
                <button :data-id="selection.id" @click="removeClick">x</button>
            </li>
        </ul>
    </div>
</template>
