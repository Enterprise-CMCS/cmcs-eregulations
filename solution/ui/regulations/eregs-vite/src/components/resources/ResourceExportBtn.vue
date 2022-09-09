<template>
    <div class="resource_btn_container">
        <button
            class="default-btn action-btn search_resource_btn"
            @click="createCSV"
        >
            Download Spreadsheet (CSV)&nbsp;&nbsp;
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
        </button>
        </div>

</template>

<script>

import exportFromJSON from 'export-from-json'
import {
    getSupplementalContentV3,

} from "../../utilities/api";
export default {
    name: "ResourceExportBtn",
    props: {
        searchQuery: {
            type: String,
            default: ""
        },
        partDict: {
            default: {}
        },
        categories: {
            type: Array,
            default: []
        },
        supCount: {
            default: 0
        }
    },
    data: {
        supplementalContent: []
    },
    computed: {

    },
    methods: {
        async createCSV(e) {
            this.supplementalContent = await this.getSupplementalContent()
            let supSort = this.supplementalContent.map(cont => {
                const content = {}
                content["category"] = cont.category.name
                content["parent"] = cont.category.parent ? cont.category.parent.name : "N/A"
                content["date"] = cont.date
                content["description"] = cont.description
                content["url"] = cont.url
                return content
            }
            )


            let fileName = 'Resources'
            let exportType = exportFromJSON.types.csv;
            exportFromJSON({ data: supSort, fileName: fileName, exportType: exportType })
        },

        async getSupplementalContent() {
            let supNum = 0;
            let page = 1;
            console.log('hi')
            let content = []
            let responseContent = []
            while (supNum < this.supCount) {
                content = await getSupplementalContentV3({
                    page: page,
                    partDict: this.partDict,
                    categories: this.categories,
                    q: this.searchQuery
                });

                page = page + 1
                supNum = supNum + 100;
                responseContent = responseContent.concat(content.results)

            }
            return responseContent
        },
    },
}
</script>
<style scoped>
.csv-button {
    border: 1px;
    border-color: black;
    background-color: #046791;
    color: white;
    padding-left: 5px;
    font-size: 14px;
    height: 36px;
    width: 246px;
}

.export-csv {
    width: 100%;
    display: block;
    padding-top: 6px;
    padding-bottom: 6px;
}
</style>
