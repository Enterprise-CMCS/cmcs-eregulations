<script setup>
import { inject, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

import useRemoveList from "composables/removeList";

const $router = useRouter();
const $route = useRoute();

const selectedParams = inject("selectedParams");
const FilterTypesDict = inject("FilterTypesDict");

const commonRemoveList = inject("commonRemoveList", []);
const additionalRemoveList = inject("policySelectionsRemoveList", []);
const removeList = commonRemoveList.concat(additionalRemoveList);

const removeClick = () => {
    const routeClone = { ...$route.query };

    const cleanedRoute = useRemoveList({
        route: routeClone,
        removeList,
    });

    $router.push({
        name: "subjects",
        query: {
            ...cleanedRoute,
        },
    });
};

const selections = ref([]);

watch(
    () => selectedParams.paramString,
    async () => {
        selections.value = selectedParams.paramsArray
            .filter((param) => FilterTypesDict[param.type])
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
                if (a.name.toLowerCase() < b.name.toLowerCase()) return -1;
                if (a.name.toLowerCase() > b.name.toLowerCase()) return 1;
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
                    :aria-label="`Remove ${selection.name} results`"
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
