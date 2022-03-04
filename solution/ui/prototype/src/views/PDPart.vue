<template>
    <body class="ds-base">
        <div id="app">
            <FlashBanner />
            <Header />
            <splitpanes>
                <pane min-size="30">
                    <left-column :title="title" :part="part" :subPart="subPart" :section="section" :structure="partContent" :navigation="navigation"/>

                </pane>
                <pane min-size="30">
                    <right-column :title="title" :part="part"/>
                </pane>
            </splitpanes>
            <Footer/>
        </div>
    </body>
</template>

<script>
import FlashBanner from "@/components/FlashBanner.vue";
import Footer from "@/components/Footer.vue";
import Header from "@/components/Header.vue";
import { Splitpanes, Pane } from 'splitpanes'
import 'splitpanes/dist/splitpanes.css'
import LeftColumn from "@/components/PDPart/LeftColumn";
import RightColumn from "../components/PDPart/RightColumn";
import { getPart, getSubPartsForPart } from "@/utilities/api";
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

    data() {
        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            subPart: this.$route.params.subPart,
            section: this.$route.params.section,
            selectedSection: null,
            structure: null,
            subPartList: [],
            sections: [],
        }
    },
    computed: {
      tocContent() {
        return this.structure?.[0];
      },
      partLabel() {
        return this.structure?.[0].label_description ?? "N/A";
      },
      partContent() {
        var results = this.structure?.[1];
        if (results && this.subPart) {
          results = results.filter(subPart => {
            return subPart.label[0] === this.subPart.split("-")[1]
          })

          if (this.section) {
            results = results[0].children.filter(section => section.label[1] === this.section)
          }
        }
        return results
      },
      navigation() {
        const results = {name:"PDpart", previous: null, next: null}
        if (this.subPart){
          results.name = "PDPart-subPart"
          const currentIndex = this.subPartList.indexOf(this.subPart.split("-")[1])
          results.previous = currentIndex > 0
              ?
              {title:this.title, part:this.part, subPart:"subPart-" + this.subPartList[currentIndex - 1]}
              :
              null;
          results.next = currentIndex < this.subPartList.length - 1
              ?
              {title:this.title, part:this.part, subPart:"subPart-" + this.subPartList[currentIndex + 1]}
              :
              null

        }
        if (this.section){
          results.name = "PDPart-section"
        }

        if (this.subPart) {
          const currentIndex = this.subPartList.indexOf(this.subPart.split("-")[1])

          results.previous = currentIndex > 0 ? "subPart-" + this.subPartList[currentIndex - 1] : null;
          results.next = currentIndex < this.subPartList.length - 1 ? "subPart-" + this.subPartList[currentIndex + 1] : null
        }
        return results
      },
    },
    async created() {
        this.$watch(
            () => this.$route.params,
            (toParams, previousParams) => {
                // react to route changes...
                if (toParams.part !== previousParams.part ||
                    toParams.subPart != previousParams.subPart ||
                    toParams.section != previousParams.section

                ) {
                    console.log("navigating")
                    this.title = toParams.title;
                    this.part = toParams.part;
                    this.subPart = toParams.subPart;
                    this.section = toParams.section;
                }
            }
        );

        try {
            this.structure = await getPart(this.title, this.part);
            this.subPartList = await getSubPartsForPart(this.part)

        } catch (error) {
            console.error(error);
        } finally {
            console.log(this.structure);
        }
    },
}
</script>

<style>

.splitpanes__pane {
  justify-content: left;
  align-items: flex-start;
  display: flex;
}

.splitpanes--vertical > .splitpanes__splitter {
  min-width: 6px;
  background: #A3E8FF;
}


</style>

