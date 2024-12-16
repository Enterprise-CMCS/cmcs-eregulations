<template>
    <section class="table-section" v-html="table"></section>
</template>

<script>
import DOMPurify from "dompurify";

export default {
    name: "table-component",

    props: {
        table_markup: {
            type: String,
            required: true,
        },
    },

    computed: {
        table() {
            return DOMPurify.sanitize(this.table_markup);
        },
    },
};
</script>
