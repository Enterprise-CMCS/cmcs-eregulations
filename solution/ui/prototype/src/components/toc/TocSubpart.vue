<template>
    <div>
        <a
            @click="doNavigation(item)"
            class="toc-link"
        >{{item.label}}</a>
        <ul class="toc-list toc-subpart-list">
            <li
                v-for="child in item.children"
                :key="child.identifier.join('-')"
                :class="child.type"

            >
                <component
                    :is="componentMap[child.type]"
                    :doNavigation="doNav"
                    :item="child"
                />
            </li>
        </ul>
    </div>
</template>

<script>

import TocSection from "@/components/toc/TocSection";
import TocSubjectGroup from "@/components/toc/TocSubjectGroup";

export default {
    name: "TocSubpart",

    components: {
        TocSection,
        TocSubjectGroup,
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
      doNav(section){
        const payload = {...section}
        payload.parent_type = 'subpart'
        payload.parent = this.item.identifier
        this.doNavigation(payload)
      }
    },
};
</script>


