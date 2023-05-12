<template>
    <div class="sidebar-container">
        <div class="title-container">
            <span v-if="selectedIdentifier" class="subsection">§</span>
            <h3 class="sidebar-title">{{ sidebarTitle }} Resources</h3>
            <v-btn
                text
                class="expand-all-btn"
                @click="expandAll"
                v-if="selectedIdentifier"
            >
                {{ expandBtnLabel }} All
            </v-btn>
        </div>
        <p class="empty-state-text" v-if="!selectedIdentifier">
            Resource links are curated and updated by a Medicaid subject matter
            expert on our team. Select a subpart or section on the left to view
            associated resources.
        </p>
        <form class="search-resources-form" @submit.prevent="search">
            <v-text-field
                v-if="selectedIdentifier"
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
        <template v-if="selectedIdentifier">
            <SupplementalContent
                :api_url="apiPath"
                :title="title"
                :part="part"
                :sections="sections"
                :subparts="subparts"
            ></SupplementalContent>
        </template>
        <div class="btn-container" v-if="selectedIdentifier">
            <ResourcesBtn
                :clickHandler="routeToResources"
                label="All"
                type="solid"
            />
        </div>
    </div>
</template>

<script>
import ResourcesBtn from "@/components/ResourcesBtn.vue";
import SupplementalContent from "legacy/eregs-component-lib/src/components/SupplementalContent.vue";
import _isArray from "lodash/isArray";

export default {
    name: "SectionResourcesSidebar",

    components: {
        ResourcesBtn,
        SupplementalContent,
    },

    props: {
        title: String,
        part: String,
        selectedIdentifier: Array,
        selectedScope: String,
        routeToResources: Function,
    },

    data() {
        return {
            apiPath: `${process.env.VUE_APP_API_URL}/v2/`,
            expanded: false,
        };
    },

    computed: {
        sections() {
            return this.selectedScope === "section"
                ? [this.selectedIdentifier]
                : [];
        },

        subparts() {
            return this.selectedScope === "subpart"
                ? [this.selectedIdentifier]
                : [];
        },
        sidebarTitle() {
            return this.selectedScope === "subpart"
                ? `${this.part} Subpart ${this.selectedIdentifier}`
                : this.selectedScope === "section"
                ? `${this.part}.${this.selectedIdentifier}`
                : "";
        },
        expandBtnLabel() {
            return this.expanded ? "Collapse" : "Expand";
        },
    },

    provide() {
        // https://v2.vuejs.org/v2/api/?redirect=true#provide-inject
        // https://stackoverflow.com/questions/60416153/making-vue-js-provide-inject-reactive
        return {
            getStateOverride: () => (this.expanded ? "expanded" : "collapsed"),
        };
    },

    methods: {
        expandAll() {
            this.expanded = !this.expanded;
        },

        search() {
            console.log("search will happen here");
        },
    },

    watch: {
        selectedIdentifier(newSelectedIdentifier) {
            this.expanded = false;
        },
    },
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$additional-font-path: "~legacy-static/fonts"; // additional Open Sans fonts
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.sidebar-container {
    .title-container {
        display: flex;
        align-items: center;
        margin-bottom: 24px;

        .subsection {
            font-size: 20px;
            font-weight: 700;
            margin: -5px 5px 0 0;
        }

        h3.sidebar-title {
            flex: 1;
            margin: 0px;
            font-size: 22px;
        }

        .expand-all-btn {
            color: $mid_gray;
            font-size: 14px;
            letter-spacing: normal;
            text-decoration: underline;
            text-transform: capitalize;
            margin-right: -16px;
        }
    }
}

.search-resources-form {
    .search-field {
        width: 430px;
        height: 40px;
        margin-bottom: 15px;

        .v-input__icon.v-input__icon--append button {
            color: $mid_blue;
        }
    }
}

.empty-state-text {
    margin-top: 20px;
    font-size: 14px;
    color: #8c8c8c;
}
</style>
