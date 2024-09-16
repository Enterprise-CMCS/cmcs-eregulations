<template>
    <div class="empty-state-container">
        <div class="empty-state-container-title">Expand your search</div>
        <div class="options-list">
            <div class="query-prompt">
                See results for
                <span class="query-emphasis">{{ query }}</span> on:
            </div>
            <ul class="external-resource-links">
                <li v-if="showInternalLink">
                    <a :href="eregsLink">{{ eregs_url_label }}</a>
                </li>
                <li>
                    <a
                        :href="ecfrLink"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                        >eCFR</a
                    >
                </li>
                <li>
                    <a
                        :href="federalRegisterLink"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                        >Federal Register</a
                    >
                </li>
                <li>
                    <a
                        :href="medicaidGovLink"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                        >Medicaid.gov</a
                    >
                </li>
                <li>
                    <a
                        :href="unitedStatesCodeLink"
                        class="external"
                        target="_blank"
                        rel="noopener noreferrer"
                        >United States Code</a
                    >
                </li>
            </ul>
        </div>
    </div>
</template>

<script>
export default {
    name: "SearchEmptyState",

    components: {},

    props: {
        eregs_url: {
            type: String,
            default: "",
        },
        eregs_url_label: {
            type: String,
            default: "",
        },
        eregs_sublabel: {
            type: String,
            default: "",
        },
        query: {
            type: String,
            required: false,
        },
        showInternalLink: {
            type: Boolean,
            default: true,
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    computed: {
        eregsLink() {
            return this.query
                ? `${this.eregs_url}?q=${this.query}`
                : this.eregs_url;
        },
        ecfrLink() {
            return `https://www.ecfr.gov/search?search[hierarchy][title]=42&search[query]=${this.query}`;
        },
        federalRegisterLink() {
            return `https://www.federalregister.gov/documents/search?conditions[agencies][]=centers-for-medicare-medicaid-services&conditions[term]=${this.query}`;
        },
        medicaidGovLink() {
            return `https://www.medicaid.gov/search-gsc?&gsc.sort=#gsc.tab=0&gsc.q=${this.query}&gsc.sort=`;
        },
        unitedStatesCodeLink() {
            return `https://uscode.house.gov/search.xhtml?edition=prelim&searchString=%28${this.query}+%28title%3A42+chapter%3A7+subchapter%3A19%29+OR+%28title%3A42+chapter%3A7+subchapter%3A21%29+%29&pageNumber=1&itemsPerPage=100&sortField=RELEVANCE&displayType=CONTEXT&action=search&q=dGVzdCAodGl0bGU6NDIgY2hhcHRlcjo3IHN1YmNoYXB0ZXI6MTkpIE9SICh0aXRsZTo0MiBjaGFwdGVyOjcgc3ViY2hhcHRlcjoyMSkg%7C%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%7C%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%7Ctrue%7C%5B%3A%3A%3A%3A%3A%3A%3A%3Afalse%3A%5D%7C%5BQWxsIEZpZWxkcw%3D%3D%3A%3BQWxsIEZpZWxkcw%3D%3D%3A%5D`;
        },
    },
};
</script>

<style lang="scss">
.empty-state-container {
    border: 2px solid $lightest_gray;

    > * {
        padding: 0 25px;
    }

    .empty-state-container-title {
        display: flex;
        align-items: center;
        height: 41px;
        font-size: $font-size-xs;
        font-weight: bold;
        text-transform: uppercase;
        background-color: $lightest_gray;
        margin-bottom: 10px;
    }

    .options-list {
        font-size: $font-size-sm;
        line-height: 18px;

        .query-emphasis {
            font-weight: bold;
        }

        ul {
            margin: 10px 0 20px;
        }
    }
}
</style>
