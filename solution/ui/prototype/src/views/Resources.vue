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
                    @select-filter="updateFilters"
                />
                <ResourcesSelections />
                <ResourcesResults />
                queryParams: {{ queryParams }}
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
        };
    },

    computed: {
        contentContainerResourcesClass() {
            return `content-container-${this.resourcesDisplay}`;
        },
    },

    methods: {
        search() {
            console.log("search will happen here");
        },
        updateFilters(payload) {
            console.log("payload", payload);
        }
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
                console.log("watching queries");
                console.log(toQueries);
                // react to route changes...
                console.log("toQueries in watch", toQueries);
            },
        },
    },

    beforeCreate() {},

    created() {},

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
