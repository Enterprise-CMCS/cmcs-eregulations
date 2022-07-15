<template>
    <body class="ds-base">
        <div id="app">
            <FlashBanner />
            <Header />
            <div class="content-container content-container-sidebar">
                <LeftColumn
                    :title="title"
                    :part="part"
                    :subPart="subPart"
                    :section="section"
                    :partLabel="partLabel"
                    :structure="partContent"
                    :tocContent="tocContent"
                    :navigation="navigation"
                    :supplementalContentCount="supplementalContentCount"
                    @view-resources="setResourcesParams"
                />
                <div class="sidebar">
                    <SectionResourcesSidebar :title="title" :part="part" />
                </div>
            </div>
            <Footer />
        </div>
    </body>
</template>

<script>
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import LeftColumn from "@/components/PDPart/LeftColumn";
import SectionResourcesSidebar from "@/components/SectionResourcesSidebar.vue";
import {
    getPart,
    getSubPartsForPart,
    getPartsList,
    getPartTOC,
    getSupplementalContentCountForPart,
} from "@/utilities/api";
export default {
    name: "Part",
    components: {
        LeftColumn,
        FlashBanner,
        Footer,
        Header,
        SectionResourcesSidebar,
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
                        this.sections = await this.getFormattedSectionsList({
                            title: this.title,
                            part: this.part,
                            subpart: this.subPart.split("-")[1],
                        });
                    }
                    this.supplementalContentCount =
                        await getSupplementalContentCountForPart(this.part);

                } catch (error) {
                    console.error(error);
                }
            },
            immediate: true,
        },
        subPart: {
            async handler() {
                this.sections = await this.getFormattedSectionsList({
                    title: this.title,
                    part: this.part,
                    subpart: this.subPart
                        ? this.subPart.split("-")[1]
                        : this.subPart,
                });
            },
        },

    },
    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            subPart: this.$route.params.subPart,
            section: this.$route.params.section,
            structure: [],
            subPartList: [],
            partsList: [],
            sections: [],
            supplementalContentCount: {},
            renderedSections: [],
        };
    },
    async created() {
        this.structure = await getPart(this.title, this.part);
    },
    computed: {
        subpartContent() {
            let subpart = this.subPart.split("-")[1];
            return this.structure[1]
                ? this.structure[1].filter(
                      (child) =>
                          child.node_type === "SUBPART" &&
                          child.label[0] === subpart
                  )
                : [];
        },
        sectionContent() {
            if (this.subpartContent && this.subpartContent.length > 0) {
                const section = this.subpartContent[0].children.find(
                    (child) =>
                        child.node_type === "SECTION" &&
                        child.label[1] === this.section
                );

                if (section) {
                    return [section];
                }

                return [
                    this.subpartContent[0].children
                        .filter((child) => child.node_type === "SUBJGRP")
                        .flatMap((sg) => sg.children)
                        .find(
                            (child) =>
                                child.node_type === "SECTION" &&
                                child.label[1] === this.section
                        ),
                ];
            }
            return this.structure?.[1].filter(
                (child) =>
                    child.node_type === "SECTION" &&
                    child.label[1] === this.section
            );
        },
        tocContent() {
            return this.structure?.[0];
        },
        partLabel() {
            return this.structure?.[0]
                ? this.structure?.[0].label_description ?? "N/A"
                : null;
        },

        partContent() {
            if (this.subPart && !this.section) {
                return this.subpartContent;
            }
            if (this.section) {
                return this.sectionContent;
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
                const currentIndex = this.subPartList.findIndex((sub) => {
                    return sub.identifier === this.subPart.split("-")[1];
                });
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
            if (payload["scope"] === "rendered") {
                this.renderedSections.push(payload["identifier"]);
                return;
            }
            this.suggestedTab = payload["scope"];
            // skip this for subparts
            if (payload["scope"] === "subpart") {
                this.suggestedSubPart = payload["identifier"]["subPart"];
                return;
            }

            // Implement response to user choosing a section or subpart here
        },
        async getFormattedSectionsList({ title, part, subpart }) {
            const toc = await getPartTOC(title, part);

            if(subpart != "undefined"){
                const totalSubpart =  toc.children.filter((sub)=> sub.identifier[0] === subpart)[0].children
                const sections = totalSubpart.filter((child)=>child.type==="section" && !child.reserved).map(sec=>sec.identifier[1])
                const groupSections = totalSubpart.filter((child)=>child.type==="subject_group").map(sub => sub.children.filter(sec => !sec.reserved).map(sec=>sec.identifier[1])).flat()

                return sections.concat(groupSections)
            }
            else{
                return []
            }

        },
    },
};
</script>
