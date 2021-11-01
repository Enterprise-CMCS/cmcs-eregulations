<template>
    <section class="table-section" v-html="table">
    </section>
</template>

<script>
export default {
    name: "table-component",

    props: {
        table_markup: {
            type: String,
            required: true,
        }

    },

    computed: {
        table() {
            return this.table_markup;
        }

    },
}
</script>
