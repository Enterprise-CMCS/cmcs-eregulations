<template>
    <div class="resource-btn-container">
        <button
            id="exportCSV"
            class="default-btn action-btn search_resource_btn desktop-btn-label"
            @click="createCSV"
        >
            <template v-if="!downloadingCSV">
                <span class="label desktop-btn-label">Download Spreadsheet (CSV)</span
                ><span class="label mobile-btn-label">CSV</span>
                <svg
                    width="18"
                    height="17"
                    viewBox="0 0 18 17"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        d="M1.78361 16.5C1.36371 16.5 0.996298 16.35 0.681372 16.05C0.366447 15.75 0.208984 15.4 0.208984 15V11.425H1.78361V15H15.4304V11.425H17.005V15C17.005 15.4 16.8475 15.75 16.5326 16.05C16.2177 16.35 15.8503 16.5 15.4304 16.5H1.78361ZM8.60699 12.675L3.54194 7.85L4.67043 6.775L7.81968 9.775V0.5H9.39431V9.775L12.5436 6.775L13.672 7.85L8.60699 12.675Z"
                        fill="white"
                    />
                </svg>
            </template>
            <template v-else>
                <simple-spinner
                    size="xs"
                ></simple-spinner>
            </template>
        </button>
    </div>
</template>

<script>
import exportFromJSON from "export-from-json";
import SimpleSpinner from "eregsComponentLib/src/components/SimpleSpinner.vue";
import { getSupplementalContent } from "utilities/api";

export default {
    name: "ResourceExportBtn",
    components: {
        SimpleSpinner,
    },
    props: {
        query: {
            type: String,
            default: "",
        },
        partDict: {
            type: Object,
            default: () => {},
        },
        categories: {
            type: Array,
            default: () => [],
        },
        supCount: {
            type: Number,
            default: 0,
        },
        title: {
            type: String,
            required: false,
            default: undefined,
        },
    },

    data() {
        return {
            supplementalContent: [],
            downloadingCSV: false,
        };
    },

    computed: {},

    methods: {
        async createCSV() {
            this.downloadingCSV = true;
            this.supplementalContent = await this.getSupplementalContent();
            const supSort = this.supplementalContent.map((cont) => {
                const content = {};
                content.category = cont.category.name;
                content.date = cont.date;
                content.description = cont.description;
                content.document_number = cont.document_number;
                content.name = cont.name;
                content.url = cont.url;
                content.Related_Regulations = this.formatLocations(
                    cont.locations
                );
                return content;
            });
            this.downloadingCSV = false;
            const fileName = "Resources";
            const exportType = exportFromJSON.types.csv;
            exportFromJSON({ data: supSort, fileName, exportType });
        },

        formatLocations(locations) {
            let locString = "";
            for (const location in locations) {
                locString = `${locString} ${locations[location].title} CFR ${locations[location].part}`;
                if (locations[location].type == "section") {
                    locString = `${locString}.${locations[location].section_id},`
                }
                else {
                    locString = `${locString} Subpart ${locations[location].subpart_id},`
                }
            }
            return locString
        },
        async getSupplementalContent() {
            let supNum = 0;
            let page = 1;
            const titleParam = this.title ? { title: this.title } : {};
            let responseContent = [];
            const content = [];
            while (supNum < this.supCount) {
                content.push(
                    getSupplementalContent({
                        page,
                        partDict:
                            Object.keys(this.partDict).length > 0
                                ? this.partDict
                                : "all",
                        categories: this.categories,
                        q: this.query,
                        fr_grouping: false,
                        ...titleParam,
                    })
                );
                page += 1;
                supNum += 100;
            }
            responseContent = await Promise.all(content);
            const ret = responseContent.map((x) => x.results).flat();
            return ret;
        },
    },
};
</script>
<style lang="scss">
.resource-btn-container {
    padding-left: 5px;

    #exportCSV {
        padding-top: 8px;
        padding-bottom: 8px;
        width: 50px;
        min-height: 18px;
        align-items: center;
        justify-content: center;

        @include screen-md {
            width: 220px;
        }

        .label {
            margin-right: 7px;

            &.desktop-btn-label {
                @include custom-max($mobile-max / 1px) {
                    display: none;
                }
            }

            &.mobile-btn-label {
                @include screen-md {
                    display: none;
                }
            }
        }

    }
}
</style>
