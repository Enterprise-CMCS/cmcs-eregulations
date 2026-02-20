<script setup>
import { ref, onMounted, onUnmounted, computed, provide, watch } from 'vue';
import clone from "lodash/clone";

import GenericDropdown from "spaComponents/dropdowns/GenericDropdown.vue";

import {
    getExternalCategories,
    getSupplementalContent,
    getChildTOC,
} from "utilities/api";
import {
    citationStringFromPartDict,
    EventCodes,
    formatResourceCategories,
    getRequestParams,
    getSectionsRecursive,
} from "utilities/utils";

import useSearchResults from "composables/searchResults.js";

import CollapseButton from "./CollapseButton.vue";
import Collapsible from "./Collapsible.vue";
import ContextBanners from "./reader-sidebar/ContextBanners.vue";
import PolicyResultsList from "spaComponents/subjects/PolicyResultsList.vue";
import ShowMoreButton from "./ShowMoreButton.vue";
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

const { policyDocList, getDocList } = useSearchResults();

const categories = ref([]);
const publicDocuments = ref({
    results: [],
    categories: [],
});
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

    if (section) {
        selectedPart.value = `§ ${section}`;
        return `citations=${props.title}.${section}`;
    } else {
        selectedPart.value = undefined;
        return "";
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

// Sort dropdown related code

const selectedSortMethod = defineModel({ default: "default", type: String });

const itemProps = (item) => {
    return {
        title: item.label,
        subtitle: item.label,
        value: item.method,
        disabled: item.disabled,
        "data-testid": `sort-${item.label.toLowerCase()}`,
    };
};

const sortOptions = ref([
    { method: "default", label: "Categories" },
    { method: "-date", label: "Newest" },
    { method: "date", label: "Oldest" },
]);

const fetchContent = async (location, sort = "default") => {
    isFetching.value = true;
    try {
        // Page size is set to 1000 to attempt to get all resources.
        // Defualt page size of 100 was omitting resources from the right sidebar.
        // Right now no single subpart hits this number so this shouldn't be an issue

        // get categories and part dict in parallel since both are needed
        // before we can render anything and they don't depend on each other
        const prefetchNeededValues = await Promise.all([
            getCategories(props.apiUrl),
            getPartDictionary(),
        ]);

        const categoryData = prefetchNeededValues[0];

        // Get subpart level counts
        const fetchSubpartResults = sort === "default"
            ? await getSupplementalContent({
                apiUrl: props.apiUrl,
                partDict: partDict.value,
                pageSize: 1000,
            })
            : await getDocList({
                apiUrl: props.apiUrl,
                forceQuerySearch: true,
                data: `${citationStringFromPartDict(partDict.value)}&${getRequestParams({ queryParams: { type: "external", sort } })}`,
            });

        resourceCount.value = sort === "default"
            ? fetchSubpartResults.count
            : clone(policyDocList.value.count);

        // Early return to get display results if default sort without location
        if (!location && sort === "default") {
            publicDocuments.value.results = fetchSubpartResults.results;
            categories.value = formatResourceCategories({
                apiUrl: props.apiUrl,
                categories: categoryData.results,
                resources: fetchSubpartResults.results,
            });
            return;
        }

        // otherwise, conditions to get display results
        let response;
        if (sort === "default") {
            response = await getSupplementalContent({
                apiUrl: props.apiUrl,
                builtCitationString: location,
                pageSize: 1000,
            })
        } else {
            await getDocList({
                apiUrl: props.apiUrl,
                forceQuerySearch: true,
                data: `${location}&${getRequestParams(
                    { queryParams: { type: "external", sort } }
                )}`
            })
            response = policyDocList.value;
        }

        publicDocuments.value.results = response.results;
        publicDocuments.value.categories = categoryData.results;
        categories.value = formatResourceCategories({
            apiUrl: props.apiUrl,
            categories: categoryData.results,
            resources: response.results,
        });
    } catch (error) {
        console.error(error);
    } finally {
        isFetching.value = false;
    }
};

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

watch(
    () => props.subparts,
    () => {
        categories.value = [];
        fetchContent();
    }
);

watch(selectedPart, () => {
    categories.value = [];
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

watch(selectedSortMethod, (newValue) => {
    categories.value = [];
    if (selectedPart.value) {
        fetchContent(
            `citations=${props.title}.${props.part}.${
                selectedPart.value.split(".")[1]
            }`,
            newValue
        );
    } else {
        fetchContent(location.value, newValue);
    }
});
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
        <slot name="public-label" />
        <div class="filter__container">
            <label class="sort__label--wrapper">
                <span class="sort__label">Sort by</span>
                <GenericDropdown
                    v-model="selectedSortMethod"
                    class="filter__select--sort"
                    :clearable="false"
                    data-testid="sort-select"
                    :item-props="itemProps"
                    :items="sortOptions"
                    :disabled="isFetching"
                />
            </label>
        </div>
        <div class="supplemental-content-container">
            Current sort method: {{ selectedSortMethod }}
            <template v-if="selectedSortMethod === 'default'">
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
            </template>
            <template v-else>
                <simple-spinner v-if="isFetching" />
                <template v-else>
                    <PolicyResultsList
                        :api-url="apiUrl"
                        :categories="publicDocuments.categories"
                        :home-url="homeUrl"
                        :results-list="publicDocuments.results.slice(0, 5)"
                        collapse-subjects
                    />
                    <template v-if="publicDocuments.results.length > 5">
                        <CollapseButton
                            name="external-chronological-collapse"
                            state="collapsed"
                            class="category-title"
                        >
                            <template #expanded>
                                <ShowMoreButton
                                    button-text="- Show Less"
                                    :count="publicDocuments.results.length"
                                />
                            </template>
                            <template #collapsed>
                                <ShowMoreButton
                                    button-text="+ Show More"
                                    :count="publicDocuments.results.length"
                                />
                            </template>
                        </CollapseButton>
                        <Collapsible
                            name="external-chronological-collapse"
                            state="collapsed"
                            class="collapse-content show-more-content"
                        >
                            <PolicyResultsList
                                :api-url="apiUrl"
                                :categories="publicDocuments.categories"
                                :home-url="homeUrl"
                                :results-list="publicDocuments.results.slice(5)"
                                collapse-subjects
                            />
                        </Collapsible>
                    </template>
                </template>
            </template>
        </div>
    </div>
    <slot name="authed-documents" :sort-method="selectedSortMethod" />
    <div class="view-all__container">
        <a
            v-if="selectedPart && subparts.length === 1 && !isFetching"
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
