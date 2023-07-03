<script setup>
import { computed, ref } from "vue";

import { acaSchema, ssaSchema } from "./schemas/tableSchemas";
import { DISPLAY_TYPES, TABLE_TYPES } from "./utils/enums";

import BodyCell from "./table-elements/BodyCell.vue";
import HeaderCell from "./table-elements/HeaderCell.vue";

const props = defineProps({
    filteredStatutes: {
        type: Array,
        required: false,
        default: () => [],
    },
    displayType: {
        validator: (value) => DISPLAY_TYPES.includes(value),
        required: false,
        default: "table",
    },
    tableType: {
        validator: (value) => TABLE_TYPES.includes(value),
        required: false,
        default: "ssa",
    },
});

const tableSchema = computed(() => {
    switch (props.tableType) {
        case "aca":
            return acaSchema;
        case "ssa":
            return ssaSchema;
        default:
            return ssaSchema;
    }
});
</script>

<template>
    <div>
        <div v-if="props.displayType == 'list'" id="statuteList">
            <div
                v-for="(statute, i) in props.filteredStatutes"
                :key="i"
                class="statute__list-item"
            >
                <table>
                    <tr
                        v-for="(column, j) in tableSchema"
                        :key="j"
                        class="table__row"
                    >
                        <HeaderCell :cell-data="column.header" />
                        <BodyCell :cell-data="column" :statute="statute" />
                    </tr>
                </table>
            </div>
        </div>
        <table v-else id="statuteTable">
            <tr class="table__row table__row--header">
                <HeaderCell
                    v-for="(column, i) in tableSchema"
                    :key="i"
                    :cell-data="column.header"
                />
            </tr>
            <tbody class="table__body">
                <tr
                    v-for="(statute, i) in props.filteredStatutes"
                    :key="i"
                    class="table__row table__row--body"
                >
                    <BodyCell
                        v-for="(column, j) in tableSchema"
                        :key="j"
                        :cell-data="column"
                        :statute="statute"
                    />
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style></style>
