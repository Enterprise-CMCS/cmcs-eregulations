<template>
    <section v-sanitize-html="table" class="table-section" />
</template>

<script>
/* eslint-disable vue/prop-name-casing */
export default {
    name: "TableComponent",

    props: {
        table_markup: {
            type: String,
            required: true,
        },
    },

    computed: {
        table() {
            return this.table_markup;
        },
    },
};
</script>
