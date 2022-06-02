<template>
    <div>
        Expand your search:
        <ul>
            <li>
                <a :href="eregs_url">eRegulations resource links</a>
                <span> (subregulatory guidance and implementation resources)</span>
            </li>
            <li>
                <a :href="ecfrLink" class="external" target="_blank">eCFR</a>
                <span> (other regulations)</span>
            </li>
            <li>
                <a :href="federalRegisterLink" class="external" target="_blank">Federal Register</a>
                <span> (documents)</span>
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    name: "SearchEmptyState",

    components: {},

    props: {
        eregs_url: {
            type: String,
            required: true,
        },
        query: {
            type: String,
            required: false,
        },
    },

    beforeCreate() {},

    created() {
        console.log(this.eregs_url);
    },

    beforeMount() {},

    mounted() {
        console.log(this.eregs_url);
        console.log(this.query);
    },

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {},

    computed: {
        ecfrLink() {
            return `https://www.ecfr.gov/search?search[hierarchy][title]=42&search[query]=${this.query}`;
        },
        federalRegisterLink() {
            return `https://www.federalregister.gov/documents/search?conditions[agencies][]=centers-for-medicare-medicaid-services&conditions[term]=${this.query}`
        }
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style>
</style>
