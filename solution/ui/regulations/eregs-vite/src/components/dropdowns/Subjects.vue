<script setup>
import SubjectSelector from "@/components/subjects/SubjectSelector.vue";

const props = defineProps({
    list: {
        type: Object,
        required: true,
    },
});

// override v-menu model to programmatically close the menu
const menuToggleModel = defineModel({
    type: Boolean,
    default: false,
});

const clickHandler = (event) => {
    const menuItemClicked =
        event.target.className.includes("sidebar-li__button");

    if (menuItemClicked) {
        menuToggleModel.value = !menuToggleModel.value;
    }
};
</script>

<template>
    <v-btn id="subjects-activator" variant="outlined" density="compact" flat
        ><span>Test {{ model }}</span></v-btn
    >
    <v-menu
        v-model="menuToggleModel"
        activator="#subjects-activator"
        :close-on-content-click="false"
        @click="clickHandler"
    >
        <SubjectSelector
            :policy-doc-subjects="list"
            class="subjects__select-container--menu"
            component-type="dropdown"
            parent="search"
        />
    </v-menu>
</template>

<style></style>
