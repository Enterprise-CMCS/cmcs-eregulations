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
const banners = ref([]);

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
    } else {
        fetchContent();
    }
    fetchContent(location.value);
    window.addEventListener("hashchange", handleHashChange);

    eventbus.on(EventCodes.SetSection, (args) => {
        selectedPart.value = args.section;
    });
    categories.value = getDefaultCategories();
    fetchBanners();
});

onUnmounted(() => {
    eventbus.off(EventCodes.SetSection);
    window.removeEventListener("hashchange", handleHashChange);
});

const handleHashChange = () => {
    location.value = parseHash(window.location.hash);
    fetchContent(location.value);
    // Also fetch context banners for the current section if present
    const sectionKey = getSectionKeyFromHash(window.location.hash);
    if (sectionKey) {
        fetchBanners(sectionKey);
    } else if (props.subparts && props.subparts.length === 1) {
        fetchBanners();
    }
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

function getSectionKeyFromHash(hash) {
    if (!hash || hash === "#main-content") return "";
    const trimmed = hash.startsWith("#") ? hash.substring(1) : hash;
    const parts = trimmed.split("-");
    if (parts.length >= 2 && !Number.isNaN(Number(parts[0])) && !Number.isNaN(Number(parts[1]))) {
        return `${props.part}.${parts[1]}`;
    }
    // Handles hashes like #75.104
    if (trimmed.includes(".")) {
        return trimmed;
    }
    return "";
}

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

async function fetchBanners(sectionKey) {
    try {
        const params = new URLSearchParams();
        params.set("title", String(props.title));
        params.set("part", String(props.part));
        if (sectionKey) {
            params.set("section", sectionKey);
        } else if (props.subparts && props.subparts.length === 1) {
            params.set("subpart", String(props.subparts[0]));
        }
        const base = props.apiUrl.replace(/\/$/, "");
        const resp = await fetch(`${base}/context-banners?${params.toString()}`);
        if (!resp.ok) throw new Error("Failed to fetch context banners");
        const data = await resp.json();
        banners.value = data.results || [];
    } catch (e) {
        console.error(e);
        banners.value = [];
    }
}

const filteredBanners = computed(() => {
    if (!banners.value || banners.value.length === 0) return [];
    // If a section is selected, show only that section's banner
    if (selectedPart.value) {
        const sectionText = selectedPart.value.replace("§", "").trim(); // e.g., "75.104" or just "104"
        const cleaned = sectionText.split(" ").pop();
        const key = cleaned.includes(".") ? cleaned : `${props.part}.${cleaned}`;
        return banners.value.filter((b) => b.section === key);
    }
    // Otherwise, on subpart view, show all banners matching the current subpart
    if (props.subparts && props.subparts.length === 1) {
        const sp = props.subparts[0];
        return banners.value.filter((b) => (b.subpart === sp) || !b.subpart);
    }
    return [];
});

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
        <div
            v-if="filteredBanners.length"
            class="context-banner"
            role="note"
            aria-label="Context"
        >
            <span class="context-banner-title">Notes</span>
            <p
                v-for="item in filteredBanners"
                :key="item.section"
                class="context-banner__item"
            >
                <template v-if="!selectedPart">
                    <strong>
                        <a :href="`#${item.section.replace('.', '-')}`">§ {{ item.section }}</a>:
                    </strong>
                    <span v-html="item.html" />
                </template>
                <template v-else>
                    <span v-html="item.html" />
                </template>
            </p>
        </div>
        <h2>Documents</h2>
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
