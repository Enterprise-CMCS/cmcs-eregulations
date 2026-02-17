<script setup>
import { onMounted, onUnmounted, ref, watch } from "vue";

import { getInternalCategories, getInternalDocs } from "utilities/api";

import {
    EventCodes,
    formatResourceCategories,
    getCurrentSectionFromHash,
    getRequestParams,
} from "utilities/utils";

import useSearchResults from "composables/searchResults.js";

import PolicyResultsList from "spaComponents/subjects/PolicyResultsList.vue";
import SimpleSpinner from "../SimpleSpinner.vue";
import SupplementalContentCategory from "../SupplementalContentCategory.vue";

import eventbus from "../../eventbus";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
    homeUrl: {
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
    sortMethod: {
        type: String,
        required: false,
        default: "default",
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
        categories = await getInternalCategories({
            apiUrl: props.apiUrl,
        });
    } catch (error) {
        console.error(error);
    }

    return categories;
};

const { policyDocList, getDocList } = useSearchResults();

const internalDocuments = ref({
    results: [],
    categories: [],
    loading: true,
});

const getDocuments = async ({ section, sort = "default" }) => {
    internalDocuments.value.loading = true;

    const rawNodeList = JSON.parse(
        document.getElementById("node_list").textContent
    );

    let locationString;

    if (section) {
        locationString = `citations=${props.title}.${props.part}.${section}`;
    } else {
        const sectionsClone = [...rawNodeList.sections];
        locationString = sectionsClone.reduce(
            (acc, currentSection) =>
                `${acc}&citations=${props.title}.${props.part}.${currentSection}`,
            `citations=${props.title}.${props.part}.${rawNodeList.subparts[0]}`
        );
    }

    try {
        const categoriesPromise = [getCategories()];
        const resultsPromise = props.sortMethod === "default"
            ? [
                getInternalDocs({
                    apiUrl: props.apiUrl,
                    requestParams: `${locationString}`,
                }),
            ]
            : [
                getDocList({
                    apiUrl: props.apiUrl,
                    forceQuerySearch: true,
                    data: `${locationString}&${getRequestParams({ queryParams: { type: "internal", sort: props.sortMethod } })}`,
                }),
            ];

        const resultsArr = await Promise.all([
            ...categoriesPromise,
            ...resultsPromise,
        ]);

        const categories = resultsArr[0];
        const documents = props.sortMethod === "default"
            ? resultsArr[1]
            : policyDocList.value;

        if (sort === "default") {
            internalDocuments.value.results = formatResourceCategories({
                categories: categories.results,
                resources: documents.results,
                apiUrl: props.apiUrl,
            });
        } else {
            internalDocuments.value.results = documents.results;
            internalDocuments.value.categories = categories.results;
        }
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

watch(() => props.sortMethod, (newValue) => {
    getDocuments({ section: selectedSection.value, sort: newValue });
});
</script>

<template>
    <div class="internal-docs__container">
        <SimpleSpinner v-if="internalDocuments.loading" />
        <template v-else>
            <template v-if="sortMethod === 'default'">
                <supplemental-content-category
                    v-for="category in internalDocuments.results"
                    :key="category.name"
                    :is-fetching="internalDocuments.loading"
                    :name="category.name"
                    :description="category.description"
                    :supplemental_content="category.supplemental_content"
                    :subcategories="category.subcategories"
                    :show-if-empty="category.show_if_empty"
                />
            </template>
            <template v-else>
                Policy Results here
                <PolicyResultsList
                    :api-url="apiUrl"
                    :categories="internalDocuments.categories"
                    :home-url="homeUrl"
                    :results-list="internalDocuments.results"
                    collapse-subjects
                />
            </template>
        </template>
    </div>
</template>

<style></style>
