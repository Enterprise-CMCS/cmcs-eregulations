<template>
    <div class="sidebar-container">
        <h3>Resources</h3>
        <p class="empty-state-text">
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
            apiPath: `${process.env.VUE_APP_API_URL}/v2/`
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
    },
};
</script>

<style>
.sidebar-container h3 {
    margin-top: 0px;
    font-size: 24px;
}

.empty-state-text {
    margin-top: 20px;
    font-size: 14px;
    color: #8c8c8c;
}
</style>
