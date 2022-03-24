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
                />
                <ResourcesResults :content="supplementalContent" />
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

import _isEmpty from "lodash/isEmpty";
import {
    getAllParts,
    getCategories,
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
                title: this.queryParams.title || 42,
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
        removeChip(payload) {
            const newQueryParams = { ...this.queryParams };
            const scopeVals = newQueryParams[payload.scope].split(",");
            const newScopeVals = scopeVals.filter(
                (val) => val !== payload.selectedIdentifier
            );
            newQueryParams[payload.scope] = newScopeVals.join(",");
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
                newQueryParams[payload.scope] = scopeVals.join(",");
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
            const queryParamsObj = { ...dataQueryParams };
            if (queryParamsObj.part) {
                if (queryParamsObj.section) {
                    queryParamsObj.sections = queryParamsObj.section.split(",");
                }
                if (queryParamsObj.subpart) {
                    queryParamsObj.subparts = queryParamsObj.subpart.split(",");
                }
                try {
                    this.supplementalContent = await getSupplementalContentNew(
                        queryParamsObj.title,
                        queryParamsObj.part,
                        queryParamsObj.sections,
                        queryParamsObj.subparts
                    );
                } catch (error) {
                    console.error(error);
                    this.supplementalContent = [];
                }
            } else {
                this.supplementalContent = [];
            }
        },
        async getFormattedPartsList() {
            const partsList = await getAllParts();
            return partsList.map((part) => {
                return {
                    name: part.name,
                    label: part.structure.children[0].children[0].children[0]
                        .label,
                };
            });
        },
        async getCategoryList() {
            const categoryList = await getCategories();
            return categoryList;
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
            async handler() {
                this.getSupplementalContent(this.queryParams);
            },
        },
    },

    beforeCreate() {},

    async created() {
        this.getSupplementalContent(this.queryParams);
        await Promise.all([
            this.getFormattedPartsList(),
            this.getCategoryList(),
        ]).then((responses) => {
            this.filters.part.listItems = responses[0];
            this.filters.resourceCategory.listItems = responses[1];
        });
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
