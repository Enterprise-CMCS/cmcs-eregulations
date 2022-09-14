<template>
    <TableComponent :table_markup="node.content"></TableComponent>
</template>

<script>
import TableComponent from "legacy/js/src/components/TableComponent.vue";

export default {
    name: "Division",

    components: {
        TableComponent
    },

    props: {
        node: {
            type: Object,
            required: true
        },
    },
}
</script>

<style></style>

