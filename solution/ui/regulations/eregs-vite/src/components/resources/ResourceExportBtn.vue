<template>
    <div class="resource_btn_container">
        <button class="default-btn action-btn search_resource_btn desktop-btn-label`" @click="createCSV">
            <span class="desktop-btn-label">Download Spreadsheet (CSV)</span><span class="mobile-btn-label">CSV</span>&nbsp;&nbsp;
            <svg width="18" height="17" viewBox="0 0 18 17" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                    d="M1.78361 16.5C1.36371 16.5 0.996298 16.35 0.681372 16.05C0.366447 15.75 0.208984 15.4 0.208984 15V11.425H1.78361V15H15.4304V11.425H17.005V15C17.005 15.4 16.8475 15.75 16.5326 16.05C16.2177 16.35 15.8503 16.5 15.4304 16.5H1.78361ZM8.60699 12.675L3.54194 7.85L4.67043 6.775L7.81968 9.775V0.5H9.39431V9.775L12.5436 6.775L13.672 7.85L8.60699 12.675Z"
                    fill="white" />
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
        query: {
            type: String,
            default: ""
        },
        partDict: {
            type: Object,
            default: () => { }
        },
        categories: {
            type: Array,
            default: () => []
        },
        supCount: {
            type: Number,
            default: 0
        }
    },

    data() {
        return {
            supplementalContent: []
        }
    },

    computed: {

    },
    
    methods: {
        async createCSV() {
            this.supplementalContent = await this.getSupplementalContent()
            const supSort = this.supplementalContent.map(cont => {
                const content = {}
                content.category = cont.category.name
                content.date = cont.date
                content.description = cont.description
                content.document_number = cont.document_number
                content.name = cont.name
                content.url = cont.url
                content.Related_Regulations = this.formatLocations(cont.locations)
                return content
            }
            )
            const fileName = 'Resources'
            const exportType = exportFromJSON.types.csv;
            exportFromJSON({ data: supSort, fileName, exportType })
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
            let responseContent = []
            const content = []
            while (supNum < this.supCount) {
                content.push(getSupplementalContentV3({
                    page,
                    partDict: this.partDict,
                    categories: this.categories,
                    q: this.query,
                    partDict:"all",
                    fr_grouping: false
                }));
                page += 1
                supNum += 100;
                

            }
            responseContent = await Promise.all(content)
            const ret = responseContent.map(x => x.results).flat()
            return ret
        },
    },
}
</script>
<style lang="scss" scoped>

.action-btn {
    padding-top: 8px;
    padding-bottom: 8px;
}
.resource_btn_container{
    padding-left:5px;
}
.export-csv {
    width: 100%;
    display: block;
    padding-top: 6px;
    padding-bottom: 6px;
}

.desktop-btn-label {
    @include custom-max($mobile-max / 1px) {
        // 767px
        display: none;
    }
}

.mobile-btn-label {
    @include screen-md {
        // 768px
        display: none;
    }
}
</style>
