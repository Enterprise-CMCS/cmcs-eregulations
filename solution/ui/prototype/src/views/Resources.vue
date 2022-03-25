<template>
    <body class="ds-base">
        <div id="app" class="resources-view">
            <Header />
            <ResourcesNav :resourcesDisplay="resourcesDisplay">
                <form class="search-resources-form" @submit.prevent="search">
                    <v-text-field
                        outlined
                        flat
                        solo
                        clearable
                        label="Search Resources"
                        type="text"
                        class="search-field"
                        append-icon="mdi-magnify"
                        hide-details
                        dense
                        @click:append="search"
                    >
                    </v-text-field>
                </form>
            </ResourcesNav>
            <div class="resources-content-container">
                <ResourcesFilters
                    :resourcesDisplay="resourcesDisplay"
                    :filters="filters"
                    @select-filter="updateFilters"
                />
                <ResourcesSelections
                    :filterParams="filterParams"
                    @chip-filter="removeChip"
                    @clear-selections="clearSelections"
                />
                <ResourcesResults
                    :isLoading="isLoading"
                    :content="supplementalContent"
                />
            </div>
        </div>
    </body>
</template>

<script>
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import ResourcesNav from "@/components/resources/ResourcesNav.vue";
import ResourcesFilters from "@/components/resources/ResourcesFilters.vue";
import ResourcesSelections from "@/components/resources/ResourcesSelections.vue";
import ResourcesResults from "@/components/resources/ResourcesResults.vue";

import _difference from "lodash/difference";
import _isEmpty from "lodash/isEmpty";
import _uniq from "lodash/uniq";

import {
    getAllParts,
    getCategories,
    getSectionObjects,
    getSubPartsForPart,
    getSupplementalContentNew,
} from "@/utilities/api";

export default {
    name: "Resources",

    components: {
        Footer,
        Header,
        ResourcesNav,
        ResourcesFilters,
        ResourcesSelections,
        ResourcesResults,
    },

    props: {},

    data() {
        return {
            isLoading: false,
            queryParams: this.$route.query,
            resourcesDisplay: this.$route.params.resourcesDisplay || "column",
            filters: {
                title: {
                    label: "Title",
                    buttonTitle: "Select Title",
                    buttonId: "select-title",
                    listType: "TitlePartList",
                    listItems: [],
                    disabled: true,
                },
                part: {
                    label: "Part",
                    buttonTitle: "Select Parts",
                    buttonId: "select-parts",
                    listType: "TitlePartList",
                    listItems: [],
                },
                subpart: {
                    label: "Subpart",
                    buttonTitle: "Select Subparts",
                    buttonId: "select-subparts",
                    listType: "SubpartList",
                    listItems: [],
                },
                section: {
                    label: "Section",
                    buttonTitle: "Select Sections",
                    buttonId: "select-sections",
                    listType: "SectionList",
                    listItems: [],
                },
                resourceCategory: {
                    label: "Resource Category",
                    buttonTitle: "Select Categories",
                    buttonId: "select-resource-categories",
                    listType: "CategoryList",
                    listItems: [],
                },
            },
            supplementalContent: [],
        };
    },

    computed: {
        contentContainerResourcesClass() {
            return `content-container-${this.resourcesDisplay}`;
        },
        filterParams() {
            return {
                title: this.queryParams.title || "42",
                part: this.queryParams.part,
                subpart: this.queryParams.subpart,
                section: this.queryParams.section,
                resourceCategory: this.queryParams.resourceCategory,
            };
        },
    },

    methods: {
        search() {
            console.log("search will happen here");
        },
        clearSelections() {
            this.$router.push({
                name: "resources",
                query: {
                    title: undefined,
                    part: undefined,
                    subpart: undefined,
                    section: undefined,
                    resourceCategory: undefined,
                },
            });
        },
        removeChip(payload) {
            const newQueryParams = { ...this.queryParams };
            const scopeVals = newQueryParams[payload.scope].split(",");
            const newScopeVals = scopeVals.filter(
                (val) => val !== payload.selectedIdentifier
            );
            newQueryParams[payload.scope] = _isEmpty(newScopeVals)
                ? undefined
                : newScopeVals.join(",");
            if (_isEmpty(newQueryParams.part)) {
                newQueryParams.title = undefined;
                newQueryParams.subpart = undefined;
                newQueryParams.section = undefined;
            }
            this.$router.push({
                name: "resources",
                query: newQueryParams,
            });
        },
        updateFilters(payload) {
            const newQueryParams = { ...this.queryParams };
            if (newQueryParams[payload.scope]) {
                const scopeVals = newQueryParams[payload.scope].split(",");
                scopeVals.push(payload.selectedIdentifier);
                const uniqScopeVals = _uniq(scopeVals);
                newQueryParams[payload.scope] = uniqScopeVals.sort().join(",");
            } else {
                newQueryParams.title = "42"; // hard coding for now
                newQueryParams[payload.scope] = payload.selectedIdentifier;
            }
            this.$router.push({
                name: "resources",
                query: newQueryParams,
            });
        },
        async getSupplementalContent(dataQueryParams) {
            this.isLoading = true;
            const queryParamsObj = { ...dataQueryParams };
            if (queryParamsObj.part) {
                queryParamsObj.part = queryParamsObj.part.split(",");
                if (queryParamsObj.section) {
                    queryParamsObj.sections = queryParamsObj.section.split(",");
                }
                if (queryParamsObj.subpart) {
                    queryParamsObj.subparts = queryParamsObj.subpart.split(",");
                }
                // map over parts and return promises to put in Promise.all
                const partPromises = queryParamsObj.part.map((part) => {
                    return getSupplementalContentNew(
                        queryParamsObj.title,
                        part,
                        queryParamsObj.sections,
                        queryParamsObj.subparts
                    );
                });

                try {
                    const resultArray = await Promise.all(partPromises);
                    this.supplementalContent = resultArray.flat();
                } catch (error) {
                    console.error(error);
                    this.supplementalContent = [];
                } finally {
                    this.isLoading = false;
                }
            } else {
                this.supplementalContent = [];
                this.isLoading = false;
            }
        },
        async getFormattedPartsList() {
            const partsList = await getAllParts();
            this.filters.part.listItems = partsList.map((part) => {
                return {
                    name: part.name,
                    label: part.structure.children[0].children[0].children[0]
                        .label,
                };
            });
        },
        async getFormattedSubpartsList(part) {
            this.filters.subpart.listItems = await getSubPartsForPart(part);
        },
        async getFormattedSectionsList(part, subpart) {
            this.filters.section.listItems = await getSectionObjects(part, subpart);
        },
        async getCategoryList() {
            this.filters.resourceCategory.listItems = await getCategories();
        },
    },

    watch: {
        "$route.params": {
            async handler(toParams, previousParams) {
                // react to route changes...
                console.log("toParams in watch", toParams);
            },
        },
        "$route.query": {
            async handler(toQueries, previousQueries) {
                this.queryParams = toQueries;
            },
        },
        queryParams: {
            // beware, some yucky code ahead...
            async handler(newParams, oldParams) {
                if (_isEmpty(newParams.part)) {
                    // only get content if a part is selected
                    // don't make supp content request here, but clear lists
                    this.filters.subpart.listItems = [];
                    this.filters.section.listItems = [];
                    this.supplementalContent = [];
                } else {
                    // always get content otherwise
                    this.getSupplementalContent(this.queryParams);

                    // logic for populating select dropdowns
                    if (_isEmpty(oldParams.part) && newParams.part) {
                        this.getFormattedSubpartsList(this.queryParams.part);
                        this.getFormattedSectionsList(
                            this.queryParams.part,
                            this.queryParams.subpart
                        );
                    } else if (
                        _isEmpty(oldParams.subpart) &&
                        newParams.subpart
                    ) {
                        this.getFormattedSectionsList(
                            this.queryParams.part,
                            this.queryParams.subpart
                        );
                    } else {
                        const oldParts = oldParams.part.split(",");
                        const newParts = newParams.part.split(",");

                        if (newParts.length > oldParts.length) {
                            const newPart = _difference(newParts, oldParts)[0];
                            this.getFormattedSubpartsList(newPart);
                            this.getFormattedSectionsList(
                                newPart,
                                this.queryParams.subpart
                            );
                        }
                    }
                }
            },
        },
    },

    beforeCreate() {},

    async created() {
        this.getFormattedPartsList();
        this.getCategoryList();

        if (this.queryParams.part) {
            this.getSupplementalContent(this.queryParams);
            this.getFormattedSubpartsList(this.queryParams.part);
            this.getFormattedSectionsList(
                this.queryParams.part,
                this.queryParams.subpart
            );
        }
    },

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

$sidebar-top-margin: 40px;

#app.resources-view {
    display: flex;
    flex-direction: column;

    .resources-content-container {
        display: flex;
        flex-direction: column;
    }

    .content-container-column {
        justify-content: center;
    }

    .content-container-sidebar {
        justify-content: space-between;
    }

    .search-resources-form {
        .search-field {
            width: calc(100% - 25px);
            height: 40px;
            margin-bottom: 50px;

            .v-input__icon.v-input__icon--append button {
                color: $mid_blue;
            }
        }
    }
}
</style>
