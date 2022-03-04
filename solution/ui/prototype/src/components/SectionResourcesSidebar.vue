<template>
    <div class="sidebar-container">
        <div class="title-container">
            <span v-if="selectedIdentifier" class="subsection">§</span>
            <h3 class="sidebar-title">
                {{ sidebarTitle }} Resources
            </h3>
            <v-btn text class="expand-all-btn" @click="expandAll" v-if="selectedIdentifier">
                {{ expandBtnLabel }} All
            </v-btn>
        </div>
        <p class="empty-state-text" v-if="!selectedIdentifier">
            Resource links are curated and updated by a Medicaid subject matter
            expert on our team. Select a subpart or section on the left to view
            associated resources.
        </p>
        <SupplementalContent
            :api_url="apiPath"
            :title="title"
            :part="part"
            :sections="sections"
            :subparts="subparts"
        ></SupplementalContent>
    </div>
</template>

<script>
import SupplementalContent from "legacy/js/src/components/SupplementalContent.vue";

export default {
    name: "SectionResourcesSidebar",

    components: {
        SupplementalContent,
    },

    props: {
        title: String,
        part: String,
        selectedIdentifier: String,
        selectedScope: String,
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

    methods: {
        expandAll() {
            console.log("clicked");
            this.expanded = !this.expanded;
        },
    },
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
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
        }
    }
}

.empty-state-text {
    margin-top: 20px;
    font-size: 14px;
    color: #8c8c8c;
}
</style>
