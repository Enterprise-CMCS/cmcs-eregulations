<template>
    <div class="subject_group">
        <span class="reserved toc-link toc-subjectgroup">{{ item.label }}</span>
        <ul class="toc-list toc-subjectgroup-list" style="padding-left: 0px;">
            <li
                v-for="child in item.children"
                :key="child.identifier.join('-')"
                :class="child.type"
                class="toc-list-item"
            >
                <component
                    :is="componentMap[child.type]"
                    :doNavigation="doNavigation"
                    :item="child"
                />
            </li>
        </ul>
    </div>
</template>

<script>

import TocSection from "@/components/toc/TocSection";
import TocSubpart from "@/components/toc/TocSubpart";

export default {
    name: "TocSubjectGroup",

    components: {
        TocSection,
        TocSubpart,
    },

    props: {
      doNavigation: {
          type: Function,
          required: true,
      },
      item: {type: Object}
    },
    data() {
        return {
            componentMap: {
              subpart: 'TocSubpart',
              section: 'TocSection',
              subject_group: 'TocSubjectGroup'
            }
        }
    },
    computed: {

    },

    methods: {
    },
};
</script>

<style>
.subject_group{
  font-size: 16px;
  font-weight: 400;
  margin-top: 25px;
}
</style>

