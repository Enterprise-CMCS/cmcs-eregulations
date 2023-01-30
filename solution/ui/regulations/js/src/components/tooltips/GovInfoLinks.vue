<template>
    <div class="gov-info-links-container">
        <div class="gov-info-links">
            <SimpleSpinner size="medium" />
        </div>
        <div class="gov-info-source">
            Section text is revised as of October 1st of each listed year. Link
            sources: <a href="https://www.govinfo.gov">GovInfo.gov</a>.
        </div>
    </div>
</template>

<script>
import SimpleSpinner from "../SimpleSpinner.vue";

export default {
    name: "GovInfoLinks",

    components: {
        SimpleSpinner,
    },

    props: {
        title: {
            type: String,
            required: true,
        },
        part: {
            type: String,
            required: true,
        },
        section: {
            type: String,
            required: true,
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {
        console.log("this.title", this.title);
        console.log("this.part", this.part);
        console.log("this.section", this.section);
    },

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            govInfoLinks: [],
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style></style>
