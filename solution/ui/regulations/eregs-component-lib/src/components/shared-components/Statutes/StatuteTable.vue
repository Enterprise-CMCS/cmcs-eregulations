<script setup>
import { computed, ref } from "vue";

const props = defineProps({
    filteredStatutes: {
        type: Array,
        required: false,
        default: () => [],
    },
    displayType: {
        validator: (value) => ["table", "list"].includes(value), // eslint-disable-line vue/valid-define-props
        default: "table",
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

const ssaCells = [
    {
        header: {
            title: "Statute Citation",
            primary: true,
        },
        body: {
            title: (statute) => `SSA Section ${statute.section}`,
            label: (statute) => `${statute.title} U. S. C. ${statute.usc}`,
            name: (statute) => `${statute.name}`,
            primary: true,
        },
    },
    {
        header: {
            title: "House.gov",
            secondary: true,
            subtitles: ["Web Page", "Effective Jun 2023"],
        },
        body: {
            url: (statute) => houseGovUrl(statute),
            text: (statute) => `${statute.usc}`,
            type: "external",
            secondary: true,
        },
    },
    {
        header: {
            title: "Statute Compilation",
            secondary: true,
            subtitles: ["PDF Document", "Amended Dec 2022"],
        },
        body: {
            url: (statute) => statuteCompilationUrl(statute),
            text: (statute) => `Title ${statute.statute_title_roman}`,
            type: "pdf",
            secondary: true,
        },
    },
    {
        header: {
            title: "US Code Annual",
            secondary: true,
            subtitles: ["PDF Document", "Effective Jan 2022"],
        },
        body: {
            url: (statute) => usCodeUrl(statute),
            text: (statute) => `${statute.usc}`,
            type: "pdf",
            secondary: true,
        },
    },
    {
        header: {
            title: "SSA.gov",
            secondary: true,
            subtitles: ["Web Page", "Amended Dec 2019"],
        },
        body: {
            url: (statute) => ssaGovUrl(statute),
            text: (statute) => `${statute.section}`,
            type: "external",
            secondary: true,
        },
    },
];
</script>

<template>
    <div>
        <div v-if="props.displayType == 'list'" id="statuteList">
            <div
                v-for="(statute, index) in props.filteredStatutes"
                :key="index"
                class="statute__list-item"
            >
                <table>
                    <tr></tr>
                </table>
            </div>
        </div>
        <table v-else id="statuteTable">
            <tr class="table__row table__row--header">
                <th
                    v-for="(column, i) in ssaCells"
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
                        v-for="(column, j) in ssaCells"
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
