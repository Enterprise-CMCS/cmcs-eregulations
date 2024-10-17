<template>
    <div>
        <h1 id="subpart-resources-heading">{{ activePart }} Resources</h1>
        <h2>Documents</h2>
        <slot name="login-banner"></slot>
        <slot name="public-label"></slot>
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
            >
            </supplemental-content-category>
            <simple-spinner v-if="isFetching"></simple-spinner>
        </div>
    </div>
    <slot name="authed-documents"></slot>
    <div class="view-all__container">
        <a
            v-if="selectedPart && subparts.length === 1"
            class="show-subpart-resources"
            data-testid="view-all-subpart-resources"
            @click="clearSection"
        >
            <span class="bold">
                View All Subpart {{ subparts[0] }} Documents</span
            >
            ({{ resourceCount }})
        </a>
    </div>
</template>

<script>
import {
    getExternalCategories,
    getSupplementalContent,
    getSubpartTOC,
} from "utilities/api";
import {
    EventCodes,
    formatResourceCategories,
    getSectionsRecursive,
} from "utilities/utils";

import SimpleSpinner from "./SimpleSpinner.vue";
import SupplementalContentCategory from "./SupplementalContentCategory.vue";

import eventbus from "../eventbus";

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
            cacheResponse: false,
        });
    } catch (error) {
        console.error(error);
    }

    return categories;
};

export default {
    components: {
        SupplementalContentCategory,
        SimpleSpinner,
    },

    props: {
        apiUrl: {
            type: String,
            required: false,
            default: "",
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
    },

    data() {
        return {
            categories: [],
            isFetching: true,
            selectedPart: undefined,
            resourceCount: 0,
            partDict: {},
        };
    },

    computed: {
        activePart() {
            if (this.selectedPart !== undefined) {
                return this.selectedPart;
            }
            return `Subpart ${this.subparts[0]}`;
        },
    },

    watch: {
        subparts() {
            this.categories = [];
            this.isFetching = true;
            this.fetchContent();
        },
        selectedPart() {
            this.categories = [];
            this.isFetching = true;
            if (this.selectedPart) {
                this.fetchContent(
                    `citations=${this.title}.${this.part}.${
                        this.selectedPart.split(".")[1]
                    }`
                );
            } else {
                this.fetchContent();
            }
        },
    },

    created() {
        let location = "";
        if (window.location.hash) {
            location = this.parseHash(window.location.hash);
        } else {
            this.fetchContent();
        }
        this.fetchContent(location);
        window.addEventListener("hashchange", this.handleHashChange);
    },
    mounted() {
        eventbus.on(EventCodes.SetSection, (args) => {
            this.selectedPart = args.section;
        });
        this.categories = getDefaultCategories();
    },
    beforeUnmount() {
        eventbus.off(EventCodes.SetSection);
    },
    unmounted() {
        window.removeEventListener("hashchange", this.handleHashChange);
    },

    methods: {
        handleHashChange() {
            const location = this.parseHash(window.location.hash);
            this.fetchContent(location);
        },
        parseHash(locationHash) {
            if (window.location.hash === "#main-content") return "";
            if (locationHash.toLowerCase().includes("appendix")) {
                this.selectedPart = undefined;
                return "";
            }

            let section = locationHash.substring(1).replace("-", ".");

            if (section.includes("-")) {
                // eslint-prefer-destructuring, kinda cool
                [section] = section.split("-");
            }

            if (Number.isNaN(section)) {
                return `citations=${this.title}.${this.part}.${section}`;
            }

            this.selectedPart = `§ ${section}`;
            return `citations=${this.title}.${section}`;
        },
        async fetchContent(location) {
            try {
                // Page size is set to 1000 to attempt to get all resources.
                // Defualt page size of 100 was omitting resources from the right sidebar.
                // Right now no single subpart hits this number so this shouldn't be an issue

                let response = "";
                if (location) {
                    response = await getSupplementalContent({
                        apiUrl: this.apiUrl,
                        builtCitationString: location,
                        pageSize: 1000,
                    });
                }
                await this.getPartDictionary();

                const results = await Promise.all([
                    getCategories(this.apiUrl),
                    getSupplementalContent({
                        apiUrl: this.apiUrl,
                        partDict: this.partDict,
                        pageSize: 1000,
                    }),
                ]);

                const categories = results[0];
                const subpartResponse = results[1];

                this.resourceCount = subpartResponse.count;

                if (response !== "") {
                    this.categories = formatResourceCategories({
                        apiUrl: this.apiUrl,
                        categories: categories.results,
                        resources: response.results,
                    });
                } else {
                    this.categories = formatResourceCategories({
                        apiUrl: this.apiUrl,
                        categories: categories.results,
                        resources: subpartResponse.results,
                    });
                }
            } catch (error) {
                console.error(error);
            } finally {
                this.isFetching = false;
            }
        },
        async getPartDictionary() {
            const sections = await getSubpartTOC({
                apiUrl: this.apiUrl,
                title: this.title,
                part: this.part,
                subPart: this.subparts[0],
            });

            const secList = getSectionsRecursive(sections);

            this.partDict[this.part] = {
                title: this.title,
                subparts: this.subparts,
                sections: secList,
            };
        },
        clearSection() {
            this.selectedPart = undefined;
            this.location = undefined;
            eventbus.emit(EventCodes.ClearSections);
        },
    },
};
</script>
