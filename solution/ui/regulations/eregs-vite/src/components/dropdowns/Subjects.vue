<script setup>
import { inject, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import SubjectSelector from "@/components/subjects/SubjectSelector.vue";

import useRemoveList from "composables/removeList";

const $router = useRouter();
const $route = useRoute();

const props = defineProps({
    list: {
        type: Object,
        required: true,
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

const menuItemClick = (event) => {
    const menuItemClicked =
        event.target.className.includes("sidebar-li__button");

    if (event.target.dataset.name) {
        buttonTitle.value = event.target.dataset.name;
    }

    if (menuItemClicked) {
        menuToggleModel.value = !menuToggleModel.value;
    }
};

const removeClick = () => {
    const routeClone = { ...$route.query };

    const cleanedRoute = useRemoveList({
        route: routeClone,
        removeList,
    });

    $router.push({
        name: props.parent,
        query: {
            ...cleanedRoute,
        },
    });
};
</script>

<template>
    <v-btn-toggle>
        <v-btn id="subjects-activator" variant="outlined" density="compact" flat
            ><span>{{ buttonTitle ?? "Choose Subject" }}</span>
        </v-btn>
        <v-btn v-if="buttonTitle" icon="mdi-close" @click="removeClick" />
    </v-btn-toggle>
    <v-menu
        v-model="menuToggleModel"
        activator="#subjects-activator"
        :close-on-content-click="false"
        @click="menuItemClick"
    >
        <SubjectSelector
            :policy-doc-subjects="list"
            class="subjects__select-container--menu"
            component-type="dropdown"
            parent
        />
    </v-menu>
</template>

<style></style>
