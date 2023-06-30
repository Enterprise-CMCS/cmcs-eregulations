<script setup>
import { computed, ref } from "vue";

const props = defineProps({
    filteredStatutes: {
        type: Array,
        required: false,
        default: () => [],
    },
});

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
            <th class="row__cell row__cell--header row__cell--primary">
                <div class="cell__title">Statute Citation</div>
            </th>
            <th class="row__cell row__cell--header row__cell--secondary">
                <div class="cell__title">House.gov</div>
                <div class="cell__subtitle">Web Page</div>
                <div class="cell__subtitle">Effective Jun 2023</div>
            </th>
            <th class="row__cell row__cell--header row__cell--secondary">
                <div class="cell__title">Statute Compilation</div>
                <div class="cell__subtitle">PDF Document</div>
                <div class="cell__subtitle">Amended Dec 2022</div>
            </th>
            <th class="row__cell row__cell--header row__cell--secondary">
                <div class="cell__title">US Code Annual</div>
                <div class="cell__subtitle">PDF Document</div>
                <div class="cell__subtitle">Effective Jan 2022</div>
            </th>
            <th class="row__cell row__cell--header row__cell--secondary">
                <div class="cell__title">SSA.gov</div>
                <div class="cell__subtitle">Web Page</div>
                <div class="cell__subtitle">Amended Dec 2019</div>
            </th>
        </tr>
        <tbody class="table__body">
            <tr
                v-for="(statute, index) in filteredStatutes"
                :key="index"
                class="table__row table__row--body"
            >
                <td
                    class="row__cell row__cell--body row__cell--primary"
                >
                    <div class="cell__title">
                        SSA Section {{ statute.section }}
                    </div>
                    <div class="cell__usc-label">
                        {{ statute.title }} U. S. C. {{ statute.usc }}
                    </div>
                    <div class="cell__name">{{ statute.name }}</div>
                </td>
                <td
                    class="row__cell row__cell--body row__cell--secondary"
                >
                    <a
                        class="external"
                        :href="houseGovUrl(statute)"
                        target="_blank"
                        rel="noopener noreferrer"
                        >{{ statute.usc }}</a
                    >
                </td>
                <td
                    class="row__cell row__cell--body row__cell--secondary"
                >
                    <a
                        class="pdf"
                        :href="statuteCompilationUrl(statute)"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        Title {{ statute.statute_title }}
                    </a>
                </td>
                <td
                    class="row__cell row__cell--body row__cell--secondary"
                >
                    <a
                        class="pdf"
                        :href="usCodeUrl(statute)"
                        target="_blank"
                        rel="noopener noreferrer"
                        >{{ statute.usc }}</a
                    >
                </td>
                <td
                    class="row__cell row__cell--body row__cell--secondary"
                >
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
