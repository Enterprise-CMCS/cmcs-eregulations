<script setup>
import { computed, ref } from "vue";

const props = defineProps({
    filteredStatutes: {
        type: Array,
        required: false,
        default: () => [],
    },
});

const tableColumnInfo = [
    {
        title: "Statute Citation",
        primary: true,
    },
    {
        title: "House.gov",
        secondary: true,
        subtitles: ["Web Page", "Effective Jun 2023"],
    },
    {
        title: "Statute Compilation",
        secondary: true,
        subtitles: ["PDF Document", "Amended Dec 2022"],
    },
    {
        title: "US Code Annual",
        secondary: true,
        subtitles: ["PDF Document", "Effective Jan 2022"],
    },
    {
        title: "SSA.gov",
        secondary: true,
        subtitles: ["Web Page", "Amended Dec 2019"],
    },
];

// URL creation methods
const houseGovUrl = (statuteObj) => {
    const { title, usc } = statuteObj;
    return `https://uscode.house.gov/view.xhtml?hl=false&edition=prelim&req=granuleid%3AUSC-prelim-title${title}-section${usc}`;
};

const usCodeUrl = (statuteObj) => {
    const { title, usc } = statuteObj;
    return `https://www.govinfo.gov/link/uscode/${title}/${usc}`;
};

const statuteCompilationUrl = (statuteObj) => {
    const { source_url } = statuteObj;
    const compsNumber = source_url
        .split("/")
        .find((str) => str.includes("COMPS"));
    return `https://www.govinfo.gov/content/pkg/${compsNumber}/pdf/${compsNumber}.pdf`;
};

const ssaGovUrl = (statuteObj) => {
    const { statute_title, section } = statuteObj;
    return `https://www.ssa.gov/OP_Home/ssact/title${statute_title}/${section}.htm`;
};
</script>

<template>
    <table id="statuteTable">
        <tr class="table__row table__row--header">
            <th
                v-for="(column, i) in tableColumnInfo"
                :key="i"
                class="row__cell row__cell--header"
                :class="{
                    'row__cell--primary': column.primary,
                    'row__cell--secondary': column.secondary,
                }"
            >
                <div class="cell__title">{{ column.title }}</div>
                <template v-if="column.subtitles">
                    <div
                        v-for="(subtitle, j) in column.subtitles"
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
                v-for="(statute, index) in filteredStatutes"
                :key="index"
                class="table__row table__row--body"
            >
                <td class="row__cell row__cell--body row__cell--primary">
                    <div class="cell__title">
                        SSA Section {{ statute.section }}
                    </div>
                    <div class="cell__usc-label">
                        {{ statute.title }} U. S. C. {{ statute.usc }}
                    </div>
                    <div class="cell__name">{{ statute.name }}</div>
                </td>
                <td class="row__cell row__cell--body row__cell--secondary">
                    <a
                        class="external"
                        :href="houseGovUrl(statute)"
                        target="_blank"
                        rel="noopener noreferrer"
                        >{{ statute.usc }}</a
                    >
                </td>
                <td class="row__cell row__cell--body row__cell--secondary">
                    <a
                        class="pdf"
                        :href="statuteCompilationUrl(statute)"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Title {{ statute.statute_title }}
                    </a>
                </td>
                <td class="row__cell row__cell--body row__cell--secondary">
                    <a
                        class="pdf"
                        :href="usCodeUrl(statute)"
                        target="_blank"
                        rel="noopener noreferrer"
                        >{{ statute.usc }}</a
                    >
                </td>
                <td class="row__cell row__cell--body row__cell--secondary">
                    <a
                        class="external"
                        :href="ssaGovUrl(statute)"
                        target="_blank"
                        rel="noopener noreferrer"
                        >{{ statute.section }}</a
                    >
                </td>
            </tr>
        </tbody>
    </table>
</template>

<style></style>
