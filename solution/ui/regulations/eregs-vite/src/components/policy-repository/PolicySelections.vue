<script setup>
import { inject, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router/composables";

import _isArray from "lodash/isArray";

const $router = useRouter();
const $route = useRoute();

const selectedParams = inject("selectedParams");
const FilterTypesDict = inject("FilterTypesDict");

const removeClick = (event) => {
    const { type, id } = event.target.dataset;
    const routeClone = { ...$route.query };
    const paramsToUpdate = routeClone[type];

    const paramsArray = _isArray(paramsToUpdate)
        ? paramsToUpdate
        : [paramsToUpdate];

    const filteredParamsArray = paramsArray.filter((paramId) => paramId !== id);

    const paramsToPush =
        filteredParamsArray.length > 0
            ? { [type]: filteredParamsArray }
            : {};

    delete routeClone[type];

    $router.push({
        name: "policy-repository",
        query: {
            ...routeClone,
            ...paramsToPush,
        },
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
                type: param.type,
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
                    :data-testid="`remove-${selection.label.toLowerCase()}-${
                        selection.id
                    }`"
                    :data-type="selection.type"
                    @click="removeClick"
                >
                    <i class="mdi mdi-close"></i>
                </button>
            </li>
        </ul>
    </div>
</template>
