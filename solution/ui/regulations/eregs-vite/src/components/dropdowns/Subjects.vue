<script setup>
import { computed, inject, ref, watchEffect } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getSubjectName } from "utilities/filters";

import SubjectSelector from "@/components/subjects/SubjectSelector.vue";

import useRemoveList from "composables/removeList";

const $router = useRouter();
const $route = useRoute();

const props = defineProps({
    list: {
        type: Object,
        required: true,
    },
    counts: {
        type: Array,
        default: () => [],
    },
    loading: {
        type: Boolean,
        default: true,
    },
    parent: {
        type: String,
        default: "search",
    },
});

const commonRemoveList = inject("commonRemoveList", []);
const removeList = commonRemoveList.concat(["subjects"]);

// override v-menu model to programmatically close the menu
const menuToggleModel = defineModel({
    type: Boolean,
    default: false,
});

const buttonTitle = ref();

const labelClasses = computed(() => ({
    "subjects-select__label": true,
    "subjects-select__label--selected": buttonTitle.value,
}));

const menuItemClick = (event) => {
    const menuItemClicked =
        event.target.className.includes("sidebar-li__button") ||
        event.target.className.includes("match__container");

    if (event.target.dataset.name) {
        buttonTitle.value = event.target.dataset.name;
    }

    if (menuItemClicked) {
        menuToggleModel.value = false;
    }
};

const clearClick = (event) => {
    // don't let click fall through to menu activator
    if (event) event.stopPropagation();

    // if menu is open, close it
    if (menuToggleModel.value === true) menuToggleModel.value = false;

    // remove subjects from query
    const routeClone = { ...$route.query };

    const cleanedRoute = useRemoveList({
        route: routeClone,
        removeList,
    });

    // push new route
    $router.push({
        name: props.parent,
        query: {
            ...cleanedRoute,
        },
    });
};

const transformedList = ref({});

watchEffect(() => {
    if (props.loading === false) {
        const clonedCounts = [...props.counts];

        const sortedCountList = clonedCounts.map((item) => {
            const subject = props.list.find(
                (subject) => subject.id == item.subject
            );

            return {
                ...subject,
                count: item.count,
            };
        });

        transformedList.value = {
            results: sortedCountList,
            loading: props.loading,
        };
    }

    if ($route.query?.subjects === undefined) {
        buttonTitle.value = undefined;

        return;
    }

    if (props.loading === false && $route.query.subjects) {
        const subjectId = $route.query.subjects;
        const subject = props.list.find((subject) => subject.id == subjectId);

        buttonTitle.value = getSubjectName(subject);
    }
});
</script>

<template>
    <v-btn
        id="subjects-activator"
        :disabled="loading"
        class="filter__select--subjects"
        variant="outlined"
        density="compact"
        flat
        :ripple="false"
    >
        <template #default>
            <span :class="labelClasses">{{
                buttonTitle ?? "Choose Subject"
            }}</span>
            <v-icon
                v-if="buttonTitle"
                class="subjects-select__clear"
                icon="mdi-close"
                size="x-large"
                @click="clearClick"
                @keydown.enter.prevent="clearClick"
            />
        </template>
        <template #append>
            <v-icon
                class="subjects-select__append-icon"
                icon="mdi-menu-swap"
            ></v-icon>
        </template>
    </v-btn>
    <v-menu
        v-model="menuToggleModel"
        activator="#subjects-activator"
        :close-on-content-click="false"
        @click="menuItemClick"
        @keydown.enter="menuItemClick"
    >
        <SubjectSelector
            :policy-doc-subjects="transformedList"
            class="subjects__select-container--menu"
            component-type="dropdown"
            placeholder="Type to filter the subject list"
            :parent
        />
    </v-menu>
</template>

<style></style>
