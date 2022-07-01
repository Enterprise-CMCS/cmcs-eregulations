<template>
    <body class="ds-base">
        <div id="app">
            <FlashBanner />
            <Header />
            <splitpanes v-on:changeSection="updateSection($event)">
                <pane min-size="30">
                    <left-column
                        :title="title"
                        :part="part"
                        :subPart="subPart"
                        :section="section"
                        :partLabel="partLabel"
                        :structure="partContent"
                        :navigation="navigation"
                        :supplementalContentCount="supplementalContentCount"
                        @view-resources="setResourcesParams"
                    />
                </pane>
                <pane min-size="30">
                    <right-column
                        :title="title"
                        :part="part"
                        :subPart="subPart"
                        :section="section"
                        :supList="supList"
                        :suggestedTab="suggestedTab"
                        :suggestedSubPart="suggestedSubPart"
                    />
                </pane>
            </splitpanes>
            <Footer />
        </div>
    </body>
</template>

<script>
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import { Splitpanes, Pane } from "splitpanes";
import "splitpanes/dist/splitpanes.css";
import LeftColumn from "@/components/PDPart/LeftColumn";
import RightColumn from "@/components/PDPart/RightColumn";
import {
    getPart,
    getSubPartsForPart,
    getPartsList,
    getPartTOC,
    getSectionsForSubPart,
    getSupplementalContentCountForPart,
    getSupplementalContentNew
} from "@/utilities/api";
export default {
    name: "Part",
    components: {
        RightColumn,
        LeftColumn,
        FlashBanner,
        Footer,
        Header,
        Splitpanes,
        Pane,
    },
    watch: {
        "$route.params": {
            async handler(toParams, previousParams) {
                // react to route changes...
                if (toParams.part !== previousParams.part) {
                    this.title = toParams.title;
                    this.part = toParams.part;
                }
                if (toParams.subPart != previousParams.subPart) {
                    this.subPart = toParams.subPart;
                }

                if (toParams.section != previousParams.section) {
                    this.section = toParams.section
                        ? String(toParams.section)
                        : undefined;
                }
            },
        },
        part: {
            async handler() {
                try {
                    this.structure = await getPart(this.title, this.part);
                    this.subPartList = await getSubPartsForPart(this.part);
                    this.partsList = await getPartsList();
                    if (this.subPart) {
                        this.sections = await this.getFormattedSectionsList({title: this.title, part: this.part, subpart: this.subPart.split('-')[1]});
                    }
                    this.supplementalContentCount =
                        await getSupplementalContentCountForPart(this.part);

                    this.supList = await getSupplementalContentNew(
                        this.title,
                        this.part,
                        this.section ? [this.section] : this.renderedSections,
                        this.subPart ? [this.subPart] : this.subPartList.map(sp => sp.identifier),
                    )

                } catch (error) {
                    console.error(error);
                }
            },
            immediate: true,
        },
        subPart:{
            async handler(){
                this.sections = await this.getFormattedSectionsList({title: this.title, part: this.part, subpart: this.subpart ? this.subPart.split('-')[1]: this.subpart});
            }
        }
    },
    async mounted(){
      try {
        this.supList = await getSupplementalContentNew(
            this.title,
            this.part,
            this.section ? [this.section] : this.renderedSections,
            this.subPart ? [this.subPart] : this.subPartList.map(sp => sp.identifier),
        )
      } catch (error) {
          console.error(error);
      }
    },
    data() {
        return {
            title: this.$route.params["title"],
            part: this.$route.params["part"],
            subPart: this.$route.params["subPart"],
            section: this.$route.params["section"],
            supList: [],
            structure: [],
            subPartList: [],
            partsList: [],
            sections: [],
            sections2:[],
            supplementalContentCount: {},
            suggestedTab:"",
            suggestedSubPart:"",
            renderedSections: []
        };
    },
    async created(){
        this.structure = await getPart(this.title, this.part);
    },
    computed: {
        subpartContent(){
            let subpart = this.subPart.split("-")[1]
            return this.structure?.[1].filter(child =>
                child.node_type === "SUBPART" && child.label[0] ===subpart
          )
        },
        sectionContent(){
          if (this.subpartContent && this.subpartContent.length > 0){
            const section = this.subpartContent[0].children.find(child =>
                child.node_type === "SECTION" && child.label[1] === this.section
            )

            if (section){
              return [section]
            }

            return [this.subpartContent[0].children.filter(child =>
                child.node_type === "SUBJGRP"
            ).map(sg => sg.children).flat(1)
            .find(child =>
                child.node_type === "SECTION" && child.label[1] === this.section
            )]

          }
          return this.structure?.[1].filter(child =>
              child.node_type === "SECTION" && child.label[1] === this.section
          )
        },
        tocContent() {
            return this.structure?.[0];
        },
        partLabel() {
            return this.structure?.[0] ? this.structure?.[0].label_description ?? "N/A" : null;
        },
        
        partContent() {
            if(this.subPart && !this.section){
                return this.subpartContent
            }
            if(this.section){
                return this.sectionContent
            }

            return this.structure?.[1] || [];
        },
        navigation() {
            const results = { name: "PDpart", previous: null, next: null };
            if (this.section) {
                results.name = "PDpart-section";
                const currentIndex = this.sections.indexOf(this.section);
                results.previous =
                    currentIndex > 0
                        ? {
                              title: this.title,
                              part: this.part,
                              subPart: this.subPart,
                              section: +this.sections[currentIndex - 1],
                          }
                        : null;
                results.next =
                    currentIndex < this.sections.length - 1
                        ? {
                              title: this.title,
                              part: this.part,
                              subPart: this.subPart,
                              section: +this.sections[currentIndex + 1],
                          }
                        : null;
            } else if (this.subPart) {
                results.name = "PDpart-subPart";
                const currentIndex = this.subPartList.findIndex(
                    sub => { return sub.identifier === this.subPart.split("-")[1]}
                );
                results.previous =
                    currentIndex > 0
                        ? {
                              title: this.title,
                              part: this.part,
                              subPart:
                                  "subPart-" +
                                  this.subPartList[currentIndex - 1].identifier,
                          }
                        : null;
                results.next =
                    currentIndex < this.subPartList.length - 1
                        ? {
                              title: this.title,
                              part: this.part,
                              subPart:
                                  "subPart-" +
                                  this.subPartList[currentIndex + 1].identifier,
                          }
                        : null;
            } else {
                results.name = "PDpart";
                const currentIndex = this.partsList.indexOf(this.part);
                results.previous =
                    currentIndex > 0
                        ? {
                              title: this.title,
                              part: this.partsList[currentIndex - 1],
                          }
                        : null;
                results.next =
                    currentIndex < this.partsList.length - 1
                        ? {
                              title: this.title,
                              part: this.partsList[currentIndex + 1],
                          }
                        : null;
            }
            return results;
        },
    },
    methods: {
        async setResourcesParams(payload) {
            if (payload["scope"] === "rendered"){
              this.renderedSections.push(payload["identifier"])
              return
            }
            this.suggestedTab = payload["scope"]
            // skip this for subparts
            if (payload["scope"] === "subpart"){
              this.suggestedSubPart = payload["identifier"]["subPart"]
              return
            }
            try {
                this.supList = await getSupplementalContentNew(
                    this.title,
                    this.part,
                    payload["identifier"]
                );
            } catch (error) {
                console.error(error);
            } finally {
                console.log(this.supList);
                this.suggestedTab = payload["scope"]
            }
            // Implement response to user choosing a section or subpart here
        },
        changeSection: function (updatedSection) {
            this.sec = updatedSection;
        },
        async getFormattedSectionsList({title, part, subpart}) {

            const toc = await getPartTOC(title, part)
            const subParts = toc.children
                .filter(child => child.type==="subpart")
                .filter(subPart => subpart ? subPart.identifier[0] === subpart: true)

            let filteredSections = subParts.map( sp => sp.children.filter(child => child.type=== 'section'))
                .flat(1)
                .map(section =>(
                     section.identifier[1]
                ))
            if (subpart === "Subpart-undefined"){
                const orphanSections = toc.children
                    .filter(child => child.type === "section")
                    .map(section =>(section.identifier[1]
                    ))
                filteredSections = filteredSections.concat(orphanSections)
            }
            const subjectGroups = subParts.map( sp => sp.children.filter(child => child.type=== 'subject_group')).flat(1)
            subjectGroups.forEach(subject_group => {
                const subPart = subject_group.parent[0]
                subject_group.children.forEach( section => {
                    filteredSections.push( section.identifier[1])
                })
            })
            filteredSections.sort((a,b) => Number(a) - Number(b))

            return filteredSections;
        },
    },
    
};
</script>

<style>
.splitpanes__pane {
    justify-content: left;
    align-items: flex-start;
    display: flex;
    position: -webkit-sticky;
    position: sticky;
    overflow: scroll;
    height: calc(100vh - 124px);
}

.splitpanes--vertical > .splitpanes__splitter {
    min-width: 6px;
    background: #a3e8ff;
}
</style>

