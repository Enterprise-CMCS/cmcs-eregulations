<script setup>
import { computed, ref } from "vue";

const props = defineProps({
    filteredStatutes: {
        type: Array,
        required: false,
        default: () => [],
    },
});

</script>

<template>
    <table id="statuteTable">
        <tr class="table__row table__row--header">
            <th class="row__cell row__cell--header row__cell--primary">
                <div class="cell__title">Statute Citation</div>
            </th>
            <th class="row__cell row__cell--header row__cell--secondary">
                <div class="cell__title">House.gov</div>
                <div class="cell__subtitle">Web Page</div>
                <div class="cell__subtitle">Updated Month Year</div>
            </th>
            <th class="row__cell row__cell--header row__cell--secondary">
                <div class="cell__title">Statute Compilation</div>
                <div class="cell__subtitle">PDF Document</div>
                <div class="cell__subtitle">Updated Month Year</div>
            </th>
            <th class="row__cell row__cell--header row__cell--secondary">
                <div class="cell__title">US Code Annual</div>
                <div class="cell__subtitle">PDF Document</div>
                <div class="cell__subtitle">Updated Month Year</div>
            </th>
            <th class="row__cell row__cell--header row__cell--secondary">
                <div class="cell__title">SSA.gov</div>
                <div class="cell__subtitle">Web Page</div>
                <div class="cell__subtitle">Updated Month Year</div>
            </th>
        </tr>
        <tbody class="table__body">
            <tr v-for="(statute, index) in filteredStatutes" class="table__row table__row--body">
                <td class="row__cell row__cell--body row__cell--primary" :key="index">
                    <div class="cell__title">SSA Section {{ statute.section }}</div>
                    <div class="cell__usc-label">{{ statute.title }} U. S. C. {{ statute.usc }}</div>
                    <div class="cell__name">{{ statute.name }}</div>
                </td>
                <td class="row__cell row__cell--body row__cell--secondary" :key="index">
                    {{ statute.usc }}
                </td>
                <td class="row__cell row__cell--body row__cell--secondary" :key="index">
                    Title {{ statute.statute_title }}
                </td>
                <td class="row__cell row__cell--body row__cell--secondary" :key="index">
                    {{ statute.usc }}
                </td>
                <td class="row__cell row__cell--body row__cell--secondary" :key="index">
                    {{ statute.section }}
                </td>
            </tr>
        </tbody>
    </table>
</template>

<style></style>
