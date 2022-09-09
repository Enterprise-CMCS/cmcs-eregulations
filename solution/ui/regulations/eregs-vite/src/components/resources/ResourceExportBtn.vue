<template>
    <div class="resource_btn_container">
        <button class="default-btn action-btn search_resource_btn" @click="createCSV">Download
            Spreadsheet(CSV) <v-icon>mdi-tray-arrow-down</v-icon></button>
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
