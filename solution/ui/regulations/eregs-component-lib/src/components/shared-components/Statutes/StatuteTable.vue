<script setup>
import { computed } from "vue";

import { acaSchema, ssaSchema } from "./schemas/tableSchemas";
import { ACT_TYPES, DISPLAY_TYPES } from "./utils/enums";

import BodyCell from "./table-elements/BodyCell.vue";
import HeaderCell from "./table-elements/HeaderCell.vue";

const props = defineProps({
    displayType: {
        validator: (value) => DISPLAY_TYPES.includes(value),
        required: false,
        default: "table",
    },
    filteredStatutes: {
        type: Array,
        required: false,
        default: () => [],
    },
    tableType: {
        validator: (value) =>
            ACT_TYPES.map((act) => Object.keys(act)[0]).includes(value),
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

// Get column dates from Django template
const getColumnDates = () => {
    if (!document.getElementById("site_config")) return {};

    const rawDates = JSON.parse(
        document.getElementById("site_config").textContent
    );

    return rawDates;
};

const columnDates = getColumnDates();
</script>

<template>
    <div>
        <div v-if="props.displayType === 'list'" id="statuteList">
            <div
                v-for="(statute, i) in props.filteredStatutes"
                :key="`statute-list-${i}`"
                class="statute__list-item"
            >
                <table>
                    <tr
                        v-for="(column, j) in tableSchema"
                        :key="`statute-list-row-${j}`"
                        class="table__row"
                    >
                        <HeaderCell
                            :cell-data="column.header"
                            :display-type="props.displayType"
                        />
                        <BodyCell :cell-data="column" :statute="statute" />
                    </tr>
                </table>
            </div>
        </div>
        <table v-else id="statuteTable">
            <tr class="table__row table__row--header">
                <HeaderCell
                    v-for="(column, i) in tableSchema"
                    :key="`statute-table-header-${i}`"
                    :cell-data="column.header"
                    :display-type="props.displayType"
                    :column-dates="columnDates"
                />
            </tr>
            <tbody class="table__body">
                <tr
                    v-for="(statute, i) in props.filteredStatutes"
                    :key="`statute-table-row-${i}`"
                    class="table__row table__row--body"
                >
                    <BodyCell
                        v-for="(column, j) in tableSchema"
                        :key="`statute-table-body-${j}`"
                        :cell-data="column"
                        :statute="statute"
                    />
                </tr>
            </tbody>
        </table>
    </div>
</template>
