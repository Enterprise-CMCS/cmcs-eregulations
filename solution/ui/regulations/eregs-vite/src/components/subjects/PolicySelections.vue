<script setup>
import { inject } from "vue";
import { useRouter, useRoute } from "vue-router";

import SelectedSubjectChip from "./SelectedSubjectChip.vue";

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
                <div class="selections__li--label">
                    <SelectedSubjectChip :subject="selectedSubject" />
                </div>
                <button
                    :aria-label="`Remove ${selectedSubject.full_name} results`"
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
