<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import { getCombinedContent, getPolicyDocCategories } from "utilities/api";

import {
    EventCodes,
    formatInternalDocCategories,
    getCurrentSectionFromHash,
} from "utilities/utils";

import SimpleSpinner from "../SimpleSpinner.vue";
import SupplementalContentCategory from "../SupplementalContentCategory.vue";

import eventbus from "../../eventbus";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
    part: {
        type: String,
        required: true,
    },
});

// What do I want to do?
// 1. Get the data from the API (categories and documents based on the section or subpart)
//   a. Get the categories ✔
//   b. Get the documents ✔
// 3. Display a spinner while the data is loading ✔
// 4. Change selected section on hashchange and on eventbus event ✔
// 5. Format categories to include data (emulate existing formatResourceCategories function)
// 6. Display the data in a tree structure using existing components

const getSectionNumber = (hash) => {
    const section = getCurrentSectionFromHash(hash);
    return section ? section.split("-")[1] : undefined;
};

const selectedSection = ref(getSectionNumber(window.location.hash));

const getCategories = async () => {
    let categories = [];

    try {
        categories = await getPolicyDocCategories({
            apiUrl: props.apiUrl,
            cacheResponse: false,
        });
    } catch (error) {
        console.error(error);
    }

    return categories;
};

const internalDocuments = ref({
    results: [],
    loading: true,
});

const getDocuments = async ({ section }) => {
    internalDocuments.value.loading = true;

    const rawNodeList = JSON.parse(
        document.getElementById("node_list").textContent
    );

    let locationString;

    if (section) {
        locationString = `locations=${props.title}.${props.part}.${section}`;
    } else {
        const sectionsClone = [...rawNodeList.sections];
        locationString = sectionsClone.reduce(
            (acc, currentSection) =>
                `${acc}&locations=${props.title}.${props.part}.${currentSection}`,
            `locations=${props.title}.${props.part}.${rawNodeList.subparts[0]}`
        );
    }

    try {
        const results = await Promise.all([
            getCategories(),
            getCombinedContent({
                apiUrl: props.apiUrl,
                cacheResponse: false,
                requestParams: `resource-type=internal&${locationString}`,
            }),
        ]);

        const categories = results[0];
        const documents = results[1];

        internalDocuments.value.results = formatInternalDocCategories({
            categories,
            docs: documents.results,
            apiUrl: props.apiUrl,
        });
    } catch (error) {
        console.error(error);
        internalDocuments.value.results = [];
    } finally {
        internalDocuments.value.loading = false;
    }
};

const handleHashChange = () => {
    selectedSection.value = getSectionNumber(window.location.hash);
};

const eventHandler = (args) => {
    const sectionNumber = args.section.split(" ")[1].split(".")[1];
    selectedSection.value = sectionNumber;
};

onMounted(() => {
    window.addEventListener("hashchange", handleHashChange);

    eventbus.on(EventCodes.SetSection, eventHandler);

    getCategories();
    getDocuments({ section: selectedSection.value });
});

onUnmounted(() => {
    window.removeEventListener("hashchange", handleHashChange);
    eventbus.off(EventCodes.SetSection, eventHandler);
});

watch(selectedSection, (newValue) => {
    getDocuments({ section: newValue });
});
</script>

<template>
    <div class="internal-docs__container">
        <SimpleSpinner v-if="internalDocuments.loading" />
        <template v-else>
            <supplemental-content-category
                v-for="category in internalDocuments.results"
                :key="category.name"
                :name="category.name"
                :description="category.description"
                :supplemental_content="category.supplemental_content"
                :sub_categories="category.sub_categories"
                :show-if-empty="category.show_if_empty"
            >
            </supplemental-content-category>
        </template>
    </div>
</template>

<style></style>
