<script setup>
import { ref, onMounted, onUnmounted, computed, provide, watch } from 'vue';
import {
    getExternalCategories,
    getSupplementalContent,
    getChildTOC,
} from "utilities/api";
import {
    EventCodes,
    formatResourceCategories,
    getSectionsRecursive,
} from "utilities/utils";

import ContextBanners from "./reader-sidebar/ContextBanners.vue";
import SimpleSpinner from "./SimpleSpinner.vue";
import SupplementalContentCategory from "./SupplementalContentCategory.vue";

import eventbus from "../eventbus";

const props = defineProps({
    apiUrl: {
        type: String,
        required: false,
        default: "",
    },
    homeUrl: {
        type: String,
        required: false,
        default: "/",
    },
    title: {
        type: String,
        required: true,
    },
    part: {
        type: String,
        required: true,
    },
    subparts: {
        type: Array,
        required: false,
        default() {
            return [];
        },
    },
});

provide("homeUrl", props.homeUrl);
provide("currentRouteName", "reader-view");

const categories = ref([]);
const isFetching = ref(true);
const selectedPart = ref(undefined);
const resourceCount = ref(0);
const partDict = ref({});
const location = ref("");

const activePart = computed(() => {
    if (selectedPart.value !== undefined) {
        return selectedPart.value;
    }
    return `Subpart ${props.subparts[0]}`;
});

watch(
    () => props.subparts,
    () => {
        categories.value = [];
        isFetching.value = true;
        fetchContent();
    }
);

watch(selectedPart, () => {
    categories.value = [];
    isFetching.value = true;
    if (selectedPart.value) {
        fetchContent(
            `citations=${props.title}.${props.part}.${
                selectedPart.value.split(".")[1]
            }`
        );
    } else {
        fetchContent();
    }
});

onMounted(() => {
    if (window.location.hash) {
        location.value = parseHash(window.location.hash);
        fetchContent(location.value);
    } else {
        fetchContent();
    }
    window.addEventListener("hashchange", handleHashChange);

    eventbus.on(EventCodes.SetSection, (args) => {
        selectedPart.value = args.section;
    });
    categories.value = getDefaultCategories();
});

onUnmounted(() => {
    eventbus.off(EventCodes.SetSection);
    window.removeEventListener("hashchange", handleHashChange);
});

const handleHashChange = () => {
    location.value = parseHash(window.location.hash);
    fetchContent(location.value);
};

const parseHash = (locationHash) => {
    if (window.location.hash === "#main-content") return "";
    if (locationHash.toLowerCase().includes("appendix")) {
        selectedPart.value = undefined;
        return "";
    }

    let section = locationHash.substring(1).replace("-", ".");

    if (section.includes("-")) {
        // eslint-prefer-destructuring, kinda cool
        [section] = section.split("-");
    }

    if (Number.isNaN(section)) {
        return `citations=${props.title}.${props.part}.${section}`;
    }

    selectedPart.value = `§ ${section}`;
    return `citations=${props.title}.${section}`;
};

const fetchContent = async (location) => {
    try {
        // Page size is set to 1000 to attempt to get all resources.
        // Defualt page size of 100 was omitting resources from the right sidebar.
        // Right now no single subpart hits this number so this shouldn't be an issue

        let response = "";
        if (location) {
            response = await getSupplementalContent({
                apiUrl: props.apiUrl,
                builtCitationString: location,
                pageSize: 1000,
            });
        }
        await getPartDictionary();

        const results = await Promise.all([
            getCategories(props.apiUrl),
            getSupplementalContent({
                apiUrl: props.apiUrl,
                partDict: partDict.value,
                pageSize: 1000,
            }),
        ]);

        const categoryData = results[0];
        const subpartResponse = results[1];

        resourceCount.value = subpartResponse.count;

        if (response !== "") {
            categories.value = formatResourceCategories({
                apiUrl: props.apiUrl,
                categories: categoryData.results,
                resources: response.results,
            });
        } else {
            categories.value = formatResourceCategories({
                apiUrl: props.apiUrl,
                categories: categoryData.results,
                resources: subpartResponse.results,
            });
        }
    } catch (error) {
        console.error(error);
    } finally {
        isFetching.value = false;
    }
};

const getPartDictionary = async () => {
    const sections = await getChildTOC({
        apiUrl: props.apiUrl,
        title: props.title,
        part: props.part,
        subPart: props.subparts[0],
    });

    const secList = getSectionsRecursive(sections);

    partDict.value[props.part] = {
        title: props.title,
        subparts: props.subparts,
        sections: secList,
    };
};

const clearSection = () => {
    selectedPart.value = undefined;
    location.value = undefined;
    eventbus.emit(EventCodes.ClearSections);
};

function getDefaultCategories() {
    if (!document.getElementById("categories")) return [];

    const rawCategories = JSON.parse(
        document.getElementById("categories").textContent
    );

    return rawCategories.map((c) => {
        const category = JSON.parse(JSON.stringify(c));
        category.subcategories = [];
        return category;
    });
}

const getCategories = async (apiUrl) => {
    let categories = [];

    try {
        categories = await getExternalCategories({
            apiUrl,
        });
    } catch (error) {
        console.error(error);
    }

    return categories;
};
</script>

<template>
    <div>
        <h1 id="subpart-resources-heading">
            {{ activePart }} Resources
        </h1>
        <ContextBanners
            :api-url="props.apiUrl"
            :title="props.title"
            :part="props.part"
            :selected-part="selectedPart"
            :subparts="props.subparts"
        />
        <slot name="login-banner" />
        <slot name="public-label" />
        <div class="supplemental-content-container">
            <supplemental-content-category
                v-for="category in categories"
                :key="category.name"
                :name="category.name"
                :subcategory="false"
                :description="category.description"
                :supplemental_content="category.supplemental_content"
                :subcategories="category.subcategories"
                :is-fetching="isFetching"
                :is-fr-link-category="category.is_fr_link_category"
                :show-if-empty="category.show_if_empty"
            />
            <simple-spinner v-if="isFetching" />
        </div>
    </div>
    <slot name="authed-documents" />
    <div class="view-all__container">
        <a
            v-if="selectedPart && subparts.length === 1"
            class="show-subpart-resources"
            data-testid="view-all-subpart-resources"
            @click="clearSection"
        >
            <span class="bold">
                View All Subpart {{ subparts[0] }} Documents</span>
            ({{ resourceCount }})
        </a>
    </div>
</template>
