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

        if (subregulatoryGuidance) {
            this.categories = subregulatoryGuidance.subcategories
                .map((cat) => `&categories=${cat.id}`)
                .join("");
        }
    },

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
                Recent Subregulatory Guidance
            </v-tab>
            <v-tab class="content-tabs" tabindex="0"> Recent Rules </v-tab>
        </v-tabs>
        <v-window v-model="tab">
            <v-window-item>
                <RecentChangesContainer
                    :api-url="apiUrl"
                    :home-url="homeUrl"
                    :categories="categories"
                    type="supplemental"
                    class="recent-supplemental-content"
                ></RecentChangesContainer>
            </v-window-item>
            <v-window-item>
                <p class="recent-rules-descriptive-text">
                    Includes 42 CFR 400, 430-460, 483, 600; 45 CFR 95, 155-156
                </p>
                <RecentChangesContainer
                    :api-url="apiUrl"
                    type="rules"
                ></RecentChangesContainer>
            </v-window-item>
        </v-window>
    </div>
</template>
