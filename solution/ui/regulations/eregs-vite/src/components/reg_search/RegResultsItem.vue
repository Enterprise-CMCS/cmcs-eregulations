<template>
    <div class="result">
        <div class="results-part">
            {{ result.part_document_title }}
        </div>
        <div class="results-section">
            <a
                :href="createResultLink(result, base)"
                v-html="removeQuotes(result.parentHeadline)"
            />
        </div>
        <div class="results-preview" v-html="result.headline" />
    </div>
</template>

<script>
import { stripQuotes } from "@/utilities/utils";

export default {
    name: "RegResultsItem",

    components: {},

    props: {
        base: {
            type: String,
            required: true,
        },
        result: {
            type: Object,
            required: true,
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

    data() {
        return {
            dataProp: "value",
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        removeQuotes(string) {
            return stripQuotes(string);
        },
        createResultLink(props, base) {
            return `${base}/${props.part_title}/${props.label[0]}/${
                props.label[1]
            }/${props.date}/?q=${props.q_list}#${props.label.join("-")}`;
        },
    },
};
</script>

<style></style>
