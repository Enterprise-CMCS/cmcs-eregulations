<template>
    <div class="sidebar-container">
        <div class="title-container">
            <span v-if="selectedIdentifier" class="subsection">§</span>
            <h3 class="sidebar-title">
                {{ sidebarTitle }} Resources
            </h3>
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
    },
};
</script>

<style lang="scss">
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

        h3 {
            margin: 0px;
            font-size: 24px;
        }
    }
}

.empty-state-text {
    margin-top: 20px;
    font-size: 14px;
    color: #8c8c8c;
}
</style>
