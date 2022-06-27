<template>
    <div v-if="structure" class="toc">
        <div class="toc-body">
            <ul class="toc-list">
                <li
                    v-for="child in structure.children"
                    :key="child.identifier.join('-')"
                    :class="child.type"
                    class="toc-group toc-list-item"
                >
                    <component
                        :is="componentMap[child.type]"
                        :doNavigation="doNavigation"
                        :item="child"
                    />

                </li>
            </ul>
        </div>
    </div>
    <div
        v-else
        class="toc"
    >
        LOADING
    </div>
</template>

<script>
import TocSubpart from "@/components/toc/TocSubpart";
import TocSection from "@/components/toc/TocSection";

export default {
    name: 'PartToc',
    components: {
        TocSubpart,
        TocSection
    },
    props: {
        structure: {
            type: Object,
            required: false
        }
    },
    data() {

        return {
            title: this.$route.params.title,
            part: this.$route.params.part,
            tabParam: this.$route.params.tab,
            queryParams: this.$route.query,
            componentMap: {
              subpart: 'TocSubpart',
              section: 'TocSection'
            }
        }
    },
    methods: {
      doNavigation(item){
          window.scrollTo(0, 0);
          const urlParams = {
                    title: this.title,
                    part: this.part,
                };
          const query = {[item.type]: item.identifier[item.identifier.length -1] }
          if (item.parent_type === "subpart"){
            query.subpart = item.parent[item.parent.length-1]
          }
          this.$router.push({
              name: "part",
              params: {
                  ...urlParams,
                  tab: item.type,
              },
              query,
          });

      }
    },
}
</script>

<style lang="scss">
.toc{
  margin-left: 90px;
  font-family: 'Open Sans',serif;
  font-style: normal;
  font-weight: 400;
  line-height: 24px;
  color: #046791;
  padding: 6px;
}
.toc-group{
  margin-top: 50px;
}
.toc-link{
  text-decoration: none;
}
.toc-group.toc-list-item.section {
  margin-left: 30px;
}
.toc-subjectgroup-list{
  padding-left: 0px;
}
.toc-subgroup{
  margin-left:20px;
}
.subpart{
  font-size: 18px;
  font-weight: 700;
  padding: 6px;
}
.toc-subjectgroup{
  padding:6px;
  font-weight: 600;
}
.toc-section{
  margin-left:50px;
  margin-top: 25px
}
.section{
  font-size: 16px;
  font-weight: 400;
  padding: 6px;
}
.toc-list li{
  list-style-type: none;
}

.toc-link{
  text-decoration: none;
}
.reserved{
  color: #5b616b;
}
.subject_group{
  font-size: 16px;
  font-weight: 400;
}


</style>

