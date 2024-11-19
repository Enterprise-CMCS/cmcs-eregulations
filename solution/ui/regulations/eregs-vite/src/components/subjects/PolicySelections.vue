<script setup>
import { inject, ref, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

import useRemoveList from "composables/removeList";

const $router = useRouter();
const $route = useRoute();

const commonRemoveList = inject("commonRemoveList", []);
const additionalRemoveList = inject("policySelectionsRemoveList", []);
const removeList = commonRemoveList.concat(additionalRemoveList);

const props = defineProps({
    selectedSubject: {
        type: Object,
        default: () => ({}),
    },
});

console.log("props.selectedSubject", props.selectedSubject);

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
</script>

<template>
    <div class="selections__container">
        <ul v-if="selectedSubject.id" class="selections__list">
            <li :key="selectedSubject.id" class="selections__li">
                {{ selectedSubject }}
                <button
                    :aria-label="`Remove ${selectedSubject.name} results`"
                    :data-id="selectedSubject.id"
                    :data-testid="`remove-subject-${selectedSubject.id}`"
                    :data-type="selectedSubject.type"
                    @click="removeClick"
                >
                    <i class="mdi mdi-close"></i>
                </button>
            </li>
        </ul>
    </div>
</template>
