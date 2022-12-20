<template>
    <div class="empty-state-container">
        <div class="empty-state-container-title">
            Expand your search:
        </div>
        <div class="options-list">
            <div class="query-prompt">
                See results for <span class="query-emphasis">{{ query }}</span> on:
            </div>
            <ul>
                <li v-if="showInternalLink">
                    <a :href="eregsLink">{{ eregs_url_label }}</a>
                    <span> ({{ eregs_sublabel }})</span>
                </li>
                <li>
                    <a :href="ecfrLink" class="external" target="_blank">eCFR</a>
                    <span> (other regulations)</span>
                </li>
                <li>
                    <a :href="federalRegisterLink" class="external" target="_blank"
                        >Federal Register</a
                    >
                    <span> (documents)</span>
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
