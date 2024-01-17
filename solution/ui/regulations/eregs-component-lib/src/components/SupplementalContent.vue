<template>
    <div>
        <a
            v-if="selectedPart && subparts.length === 1"
            class="show-subpart-resources"
            data-testid="view-all-subpart-resources"
            @click="clearSection"
        >
            <span class="bold">
                View All Subpart {{ subparts[0] }} Resources</span
            >
            ({{ resourceCount }})
        </a>
        <h2 id="subpart-resources-heading">{{ activePart }} Resources</h2>
        <slot name="login-banner"></slot>
        <div v-if="resourceDisplay" class="resource_btn_container">
            <a
                :href="resourceLink"
                class="default-btn action-btn search_resource_btn"
                >Search These Resources</a
            >
        </div>
        <slot name="public-label"></slot>
        <div class="supplemental-content-container">
            <supplemental-content-category
                v-for="category in categories"
                :key="category.name"
                :name="category.name"
                :subcategory="false"
                :description="category.description"
                :supplemental_content="category.supplemental_content"
                :sub_categories="category.sub_categories"
                :is-fetching="isFetching"
                :is-fr-doc-category="category.is_fr_doc_category"
                :show-if-empty="category.show_if_empty"
            >
            </supplemental-content-category>
            <simple-spinner v-if="isFetching"></simple-spinner>
        </div>
    </div>
</template>

<script>
import { getSupplementalContent, getSubpartTOC } from "utilities/api";
import { EventCodes, formatResourceCategories } from "utilities/utils";

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
        category.sub_categories = [];
        return category;
    });
}

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
        resourcesUrl: {
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
        sections: {
            type: Array,
            required: false,
            default: () => [],
        },
        subparts: {
            type: Array,
            required: false,
            default() {
                return [];
            },
        },
        resourceDisplay: {
            type: Boolean,
            required: false,
            default: false,
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
        params_array() {
            return [
                ["sections", this.sections],
                ["subparts", this.subparts],
            ];
        },

        activePart() {
            if (this.selectedPart !== undefined) {
                return this.selectedPart;
            }
            return `Subpart ${this.subparts[0]}`;
        },

        resourceLink() {
            let qString = `${this.resourcesUrl}?title=${this.title}&part=${this.part}`;

            if (this.activePart.includes("Subpart")) {
                qString = `${qString}&subpart=${this.part}-${this.params_array[1][1]}`;
                const sections = `${this.part}-${this.sections.join(
                    `,${this.part}-`
                )}`;
                return `${qString}&section=${sections}`;
            }
            const selection = this.activePart.split(" ")[1].replace(".", "-");
            return `${qString}&section=${selection}`;
        },
    },

    watch: {
        sections() {
            this.categories = [];
            this.isFetching = true;
            this.fetchContent();
        },
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
                    `locations=${this.title}.${this.part}.${
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
    beforeDestroy() {
        eventbus.off(EventCodes.SetSection);
    },
    destroyed() {
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
                return `locations=${this.title}.${this.part}.${section}`;
            }

            this.selectedPart = `§ ${section}`;
            return `locations=${this.title}.${section}`;
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
                        builtLocationString: location,
                        pageSize: 1000,
                    });
                }
                await this.getPartDictionary();

                const subpartResponse = await getSupplementalContent({
                    apiUrl: this.apiUrl,
                    partDict: this.partDict,
                    pageSize: 1000,
                });

                this.resourceCount = subpartResponse.count;

                const rawCategories = JSON.parse(
                    document.getElementById("categories").textContent
                );

                if (response !== "") {
                    this.categories = formatResourceCategories({
                        apiUrl: this.apiUrl,
                        categories: rawCategories,
                        resources: response.results
                    });
                } else {
                    this.categories = formatResourceCategories({
                        apiUrl: this.apiUrl,
                        categories: rawCategories,
                        resources: subpartResponse.results
                    });
                }
            } catch (error) {
                console.error(error);
            } finally {
                this.isFetching = false;
            }
        },
        async getPartDictionary() {
            const sections = await getSubpartTOC(
                this.apiUrl,
                this.title,
                this.part,
                this.subparts[0]
            );
            const secList = sections.map((section) => section.identifier[1]);
            this.partDict[this.part] = {
                title: this.title,
                subparts: this.subparts,
                sections: secList,
            };
        },
        clearSection() {
            this.selectedPart = undefined;
            this.location = undefined;
        },
    },
};
</script>

<style lang="scss">
.resource_btn_container {
    padding: 5px 12px 5px 0px;
}

.search_resource_btn {
    width: fit-content;
    line-height: 18px;
    padding: 5px 12px 5px 12px;
    border: none;
    text-decoration: none;
}

a.search_resource_btn:visited {
    color: white;
}

a.search_resource_btn:hover {
    color: white;
}
</style>
