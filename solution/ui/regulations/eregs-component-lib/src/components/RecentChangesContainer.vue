<script>
import { getRecentResources } from "utilities/api";

import RelatedRuleList from "./RelatedRuleList.vue";
import SimpleSpinner from "./SimpleSpinner.vue";
import RecentSupplementalContent from "./RecentSupplementalContent.vue";

export default {
    name: "DefaultName",

    components: {
        RelatedRuleList,
        SimpleSpinner,
        RecentSupplementalContent,
    },

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
        type: {
            type: String,
            required: false,
            default: "rules",
        },
        categories: {
            type: String,
            required: false,
            default: null,
        },
    },

    async created() {
        if (this.type !== "supplemental") {
            this.getRules();
        }
    },

    data() {
        return {
            loading: true,
            rules: [],
        };
    },

    provide() {
        return {
            homeUrl: this.homeUrl,
            itemTitleLineLimit: 9,
            currentRouteName: "homepage",
        };
    },

    methods: {
        async getRules(catsObj = {}) {
            const args = {
                page: 1,
                pageSize: 5,
                type: this.type,
                ...catsObj,
            };
            const rulesResponse = await getRecentResources({ apiURL: this.apiUrl, ...args });

            this.rules = rulesResponse.results;
            this.loading = false;
        },
    },

    watch: {
        async categories(newCats, oldCats) {
            if (oldCats === null) {
                this.getRules({ categories: newCats });
            }
        },
    },
};
</script>
<template>
    <div class="rules-container">
        <SimpleSpinner v-if="loading" />
        <RelatedRuleList
            v-if="!loading && type != 'supplemental'"
            :rules="rules"
        />
        <RecentSupplementalContent
            v-if="!loading && type == 'supplemental'"
            :supplemental-content="rules"
            :limit="5"
        />
    </div>
</template>
