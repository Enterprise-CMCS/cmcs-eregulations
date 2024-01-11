<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import { getCombinedContent, getPolicyDocCategories } from "utilities/api";

import { EventCodes, getCurrentSectionFromHash } from "utilities/utils";

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
//   b. Get the documents
// 2. Format categories to include data (emulate existing formatResourceCategories function)
// 3. Display the data in a tree structure using existing components

const getSectionNumber = (hash) => {
    const section = getCurrentSectionFromHash(hash);
    return section ? section.split("-")[1] : undefined;
};

const selectedSection = ref(getSectionNumber(window.location.hash));

const internalDocCategories = ref({
    results: [],
    loading: true,
});

const getCategories = async () => {
    internalDocCategories.value.loading = true;

    try {
        const categories = await getPolicyDocCategories({
            apiUrl: props.apiUrl,
            cacheResponse: false,
        });
        internalDocCategories.value.results = categories;
    } catch (error) {
        console.error(error);
    } finally {
        internalDocCategories.value.loading = false;
    }
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
        const documents = await getCombinedContent({
            apiUrl: props.apiUrl,
            cacheResponse: false,
            requestParams: `resource-type=internal&${locationString}`,
        });
        internalDocuments.value.results = documents;
    } catch (error) {
        console.error(error);
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
        <SimpleSpinner
            v-if="internalDocCategories.loading || internalDocuments.loading"
        />
        <template v-else>
            Selected Section: {{ selectedSection }}
            {{ internalDocuments.results }}
            <template v-for="category in internalDocCategories.results">
                {{ category.parent }}
            </template>
        </template>
    </div>
</template>

<style></style>
