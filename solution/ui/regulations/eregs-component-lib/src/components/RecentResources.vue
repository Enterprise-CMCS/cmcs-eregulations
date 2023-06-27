<script>
import RecentChangesContainer from "./RecentChangesContainer.vue";

export default {
    name: "RecentResources",

    props: {
        apiUrl: {
            type: String,
            required: true,
        },
        resourceLink: {
            type: String,
            required: true,
        },
        frDocLink: {
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
        <v-tabs v-model="tab" slider-size="4" grow>
            <v-tab class="content-tabs"> Recent Subregulatory Guidance </v-tab>
            <v-tab class="content-tabs"> Recent Rules </v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
            <v-tab-item>
                <p class="recent-rules-descriptive-text">
                    Includes 42 CFR 400, 430-460, 600, and 45 CFR 95
                </p>
                <RecentChangesContainer
                    :api-url="apiUrl"
                    type="supplemental"
                ></RecentChangesContainer>
                <a :href="resourceLink" class="action-btn default-btn link-btn"
                    >View More Guidance</a
                >
            </v-tab-item>
            <v-tab-item>
                <p class="recent-rules-descriptive-text">
                    Includes 42 CFR 400, 430-460, 600, and 45 CFR 95
                </p>
                <RecentChangesContainer
                    :api-url="apiUrl"
                    type="rules"
                ></RecentChangesContainer>
                <a :href="frDocLink" class="action-btn default-btn link-btn"
                    >View More Changes</a
                >
            </v-tab-item>
        </v-tabs-items>
    </div>
</template>
