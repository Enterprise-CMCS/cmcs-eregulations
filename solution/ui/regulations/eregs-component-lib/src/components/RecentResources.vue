<script>
import RecentChangesContainer from "./RecentChangesContainer.vue";

export default {
    name: "RecentResources",

    props: {
        api_url: {
            type: String,
            required: true,
        },
        resource_link: {
            type: String,
            required: true,
        },
        fr_doc_link: {
            type: String,
            required: true,
        },
    },
    data() {
        return {
            tab: null,
        };
    },
    components: {
        RecentChangesContainer,
    },
};
</script>

<template>
    <div>
        <v-tabs v-model="tab">
            <v-tab class="content-tabs"> Recent Subregulatory Guidance </v-tab>
            <v-tab class="content-tabs"> Recent Rules </v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
            <v-tab-item>
                <p class="recent-rules-descsriptive-text">
                    Includes 42 CFR 400, 430-460 and 45 CFR 75, 95, 155
                </p>
                <RecentChangesContainer
                    :apiUrl="api_url"
                    type="supplemental"
                ></RecentChangesContainer>
                <a :href="resource_link" class="action-btn default-btn link-btn"
                    >View More Guidance</a
                >
            </v-tab-item>
            <v-tab-item>
                <p class="recent-rules-descriptive-text">
                    Includes 42 CFR 400, 430-460 and 45 CFR 75, 95, 155
                </p>
                <RecentChangesContainer
                    :apiUrl="api_url"
                    type="rules"
                ></RecentChangesContainer>
                <a :href="fr_doc_link" class="action-btn default-btn link-btn"
                    >View More Changes</a
                >
            </v-tab-item>
        </v-tabs-items>
    </div>
</template>
