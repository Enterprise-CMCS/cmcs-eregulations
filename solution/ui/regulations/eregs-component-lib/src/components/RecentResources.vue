<script setup>
import { ref, watchEffect } from "vue";

import useCategories from "composables/categories";

import RecentChangesContainer from "./RecentChangesContainer.vue";
import SimpleSpinner from "./SimpleSpinner.vue";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
    homeUrl: {
        type: String,
        required: false,
        default: "/",
    },
});

const categoriesResults = useCategories({ apiUrl: props.apiUrl });

const tab = ref(0);
const categories = ref(null);

watchEffect(() => {
    const subregulatoryGuidance = categoriesResults.value.data.filter(
        (cat) => cat.name === "Subregulatory Guidance"
    )[0];

    if (subregulatoryGuidance) {
        categories.value = subregulatoryGuidance.subcategories
            .map((cat) => `&categories=${cat.id}`)
            .join("");
    }
});
</script>

<template>
    <div>
        <v-tabs v-model="tab" grow>
            <v-tab class="content-tabs" tabindex="0">
                Recent Subregulatory Guidance
            </v-tab>
            <v-tab class="content-tabs" tabindex="0">
                Recent Rules
            </v-tab>
        </v-tabs>
        <v-window v-model="tab">
            <v-window-item>
                <div v-if="!categories" class="rules-container">
                    <SimpleSpinner />
                </div>
                <RecentChangesContainer
                    v-else
                    :api-url="apiUrl"
                    :home-url="homeUrl"
                    :categories="categories"
                    type="supplemental"
                    class="recent-supplemental-content"
                />
            </v-window-item>
            <v-window-item>
                <p class="recent-rules-descriptive-text">
                    Includes 42 CFR 400, 430-460, 483, 600; 45 CFR 95, 155-156
                </p>
                <RecentChangesContainer
                    :api-url="apiUrl"
                    type="rules"
                />
            </v-window-item>
        </v-window>
    </div>
</template>
