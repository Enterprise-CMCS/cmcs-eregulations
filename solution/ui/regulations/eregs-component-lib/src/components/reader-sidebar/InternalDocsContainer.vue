<script setup>
import { onMounted, onUnmounted, ref, watch } from "vue";

import { getCombinedContent, getPolicyDocCategories } from "utilities/api";

import {
    EventCodes,
    formatResourceCategories,
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
                requestParams: `resource-type=internal&${locationString}`,
            }),
        ]);

        const categories = results[0];
        const documents = results[1];

        internalDocuments.value.results = formatResourceCategories({
            categories,
            resources: documents.results,
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

const sectionChangeHandler = (args) => {
    const sectionNumber = args.section.split(" ")[1].split(".")[1];
    selectedSection.value = sectionNumber;
};

const clearSectionsHandler = () => {
    selectedSection.value = undefined;
};

onMounted(() => {
    window.addEventListener("hashchange", handleHashChange);

    eventbus.on(EventCodes.SetSection, sectionChangeHandler);
    eventbus.on(EventCodes.ClearSections, clearSectionsHandler);

    getCategories();
    getDocuments({ section: selectedSection.value });
});

onUnmounted(() => {
    window.removeEventListener("hashchange", handleHashChange);

    eventbus.off(EventCodes.SetSection, sectionChangeHandler);
    eventbus.off(EventCodes.ClearSections, clearSectionsHandler);
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
                :is-fetching="internalDocuments.loading"
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
