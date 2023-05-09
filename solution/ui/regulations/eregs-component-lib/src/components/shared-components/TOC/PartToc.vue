<template>
    <div v-if="structure" class="toc">
        <div class="toc-body">
            <ul class="toc-list" style="padding:0">
                <li
                    v-for="child in structure.children"
                    :key="child.identifier.join('-')"
                    :class="child.type"
                    class="toc-group toc-list-item"
                >
                    {{ child.children.length }}
                    <component
                        :is="componentMap[child.type]"
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
// import TocSubpart from "@/components/toc/TocSubpart";
import TocSection from "sharedComponents/TOC/TocSection.vue";

export default {
    name: 'PartToc',
    components: {
        //TocSubpart,
        TocSection
    },
    props: {
        structure: {
            type: Object,
            required: false
        },
        navName : {
          type: String,
          required: false,
          default: 'part'
        }
    },
    data() {
        return {
            componentMap: {
              //subpart: 'TocSubpart',
              section: 'TOCSection'
            }
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

