<script>
import { getExternalCategories } from "utilities/api";

import RecentChangesContainer from "./RecentChangesContainer.vue";

export default {
    name: "RecentResources",

    props: {
        apiUrl: {
            type: String,
            required: true,
        },
        homeUrl: {
            type: String,
            required: false,
            default: "/",
        },
    },

    async created() {
        const categoriesResult = await getExternalCategories({
            apiUrl: this.apiUrl,
        });

        const subregulatoryGuidance = categoriesResult.results.filter(
            (cat) => cat.name === "Subregulatory Guidance"
        )[0];

        // Remove the filtering logic to show all categories
        this.categories = categoriesResult.results
            .map((cat) => `&categories=${cat.id}`)
            .join("");

    data() {
        return {
            tab: 0,
            categories: null,
        };
    },

    components: {
        RecentChangesContainer,
    },
};
</script>

<template>
    <div>
        <v-tabs v-model="tab" grow>
            <v-tab class="content-tabs" tabindex="0">
                Recent Resources
            </v-tab>
            <v-tab class="content-tabs" tabindex="0">
                Recent Rules
            </v-tab>
        </v-tabs>
        <v-window v-model="tab">
            <v-window-item>
                <RecentChangesContainer
                    :api-url="apiUrl"
                    :home-url="homeUrl"
                    :categories="categories"
                    type="supplemental"
                    class="recent-supplemental-content"
                />
            </v-window-item>
            <v-window-item>
                <p class="recent-rules-descriptive-text">
                    Includes selected parts of 5 CFR
                </p>
                <RecentChangesContainer
                    :api-url="apiUrl"
                    type="rules"
                />
            </v-window-item>
        </v-window>
    </div>
</template>
