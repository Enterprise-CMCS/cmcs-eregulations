<script setup>
import { computed, ref } from "vue";

import { ssaSchema } from "./schemas/tableSchemas";
import { DISPLAY_TYPES, TABLE_TYPES } from "./utils/enums";

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
                        <th
                            class="row__cell row__cell--header"
                            :class="{
                                'row__cell--primary': column.header.primary,
                                'row__cell--secondary': column.header.secondary,
                            }"
                        >
                            <div class="cell__title">
                                {{ column.header.title }}
                            </div>
                            <template v-if="column.header.subtitles">
                                <div
                                    v-for="(subtitle, j) in column.header
                                        .subtitles"
                                    :key="j"
                                    class="cell__subtitle"
                                >
                                    {{ subtitle }}
                                </div>
                            </template>
                        </th>
                        <td
                            class="row__cell row__cell--body"
                            :class="{
                                'row__cell--primary': column.header.primary,
                                'row__cell--secondary': column.header.secondary,
                            }"
                        >
                            <template v-if="column.body.primary">
                                <div class="cell__title">
                                    {{ column.body.title(statute) }}
                                </div>
                                <div class="cell__usc-label">
                                    {{ column.body.label(statute) }}
                                </div>
                                <div class="cell__name">
                                    {{ column.body.name(statute) }}
                                </div>
                            </template>
                            <template v-else>
                                <a
                                    :class="column.body.type"
                                    :href="column.body.url(statute)"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    >{{ column.body.text(statute) }}</a
                                >
                            </template>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
        <table v-else id="statuteTable">
            <tr class="table__row table__row--header">
                <th
                    v-for="(column, i) in tableSchema"
                    :key="i"
                    class="row__cell row__cell--header"
                    :class="{
                        'row__cell--primary': column.header.primary,
                        'row__cell--secondary': column.header.secondary,
                    }"
                >
                    <div class="cell__title">{{ column.header.title }}</div>
                    <template v-if="column.header.subtitles">
                        <div
                            v-for="(subtitle, j) in column.header.subtitles"
                            :key="j"
                            class="cell__subtitle"
                        >
                            {{ subtitle }}
                        </div>
                    </template>
                </th>
            </tr>
            <tbody class="table__body">
                <tr
                    v-for="(statute, i) in props.filteredStatutes"
                    :key="i"
                    class="table__row table__row--body"
                >
                    <td
                        v-for="(column, j) in tableSchema"
                        :key="j"
                        class="row__cell row__cell--body"
                        :class="{
                            'row__cell--primary': column.body.primary,
                            'row__cell--secondary': column.body.secondary,
                        }"
                    >
                        <template v-if="column.body.primary">
                            <div class="cell__title">
                                {{ column.body.title(statute) }}
                            </div>
                            <div class="cell__usc-label">
                                {{ column.body.label(statute) }}
                            </div>
                            <div class="cell__name">
                                {{ column.body.name(statute) }}
                            </div>
                        </template>
                        <template v-else>
                            <a
                                :class="column.body.type"
                                :href="column.body.url(statute)"
                                target="_blank"
                                rel="noopener noreferrer"
                                >{{ column.body.text(statute) }}</a
                            >
                        </template>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<style></style>
