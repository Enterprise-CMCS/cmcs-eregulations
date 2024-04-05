<script>
import { getCategories } from "utilities/api";

import RecentChangesContainer from "./RecentChangesContainer.vue";

export default {
    name: "RecentResources",

    props: {
        apiUrl: {
            type: String,
            required: true,
        },
    },

    async created() {
        const categoriesResult = await getCategories(this.apiUrl);
        this.categories = categoriesResult
            .flatMap((cat) =>
                cat.parent?.name === "Subregulatory Guidance"
                    ? `&categories=${cat.id}`
                    : []
            )
            .join("");

        this.categoryNames = categoriesResult
            .flatMap((cat) =>
                cat.parent?.name === "Subregulatory Guidance" ? cat.name : []
            )
            .join(",");
    },

    data() {
        return {
            tab: 0,
            categories: null,
            categoryNames: null,
        };
    },

    components: {
        RecentChangesContainer,
    },
};
</script>

<template>
    <div>
        <v-tabs grow v-model="tab">
            <v-tab class="content-tabs" tabindex="0">
                Recent Subregulatory Guidance
            </v-tab>
            <v-tab class="content-tabs" tabindex="0"> Recent Rules </v-tab>
        </v-tabs>
        <v-window v-model="tab">
            <v-window-item>
                <p class="recent-rules-descriptive-text">
                    Includes 42 CFR 400, 430-460, 600, and 45 CFR 95
                </p>
                <RecentChangesContainer
                    :api-url="apiUrl"
                    :categories="categories"
                    type="supplemental"
                ></RecentChangesContainer>
            </v-window-item>
            <v-window-item>
                <p class="recent-rules-descriptive-text">
                    Includes 42 CFR 400, 430-460, 600, and 45 CFR 95
                </p>
                <RecentChangesContainer
                    :api-url="apiUrl"
                    type="rules"
                ></RecentChangesContainer>
            </v-window-item>
        </v-window>
    </div>
</template>
