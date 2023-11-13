<template>
    <div class="content-container">
        <div
            v-if="structure"
            class="content reg-text"
            :class="resourcesClass"
        >
            <Node
                v-for="item in structure"
                :node="item"
                :key="item.title"
                :resourceParamsEmitter="emitResourcesParams"
                :showResourceButtons="showResourceButtons"
                :supplementalContentCount="supplementalContentCount"
                :title="title"
                :part="part"
                :subpart="subpart"
                :headerLinks="headerLinks"
            />
        </div>
        <div v-else>
            <SimpleSpinner />
        </div>
    </div>
</template>

<script>
import Node from "@/components/node_types/Node.vue";
import SimpleSpinner from "legacy/eregs-component-lib/src/components/SimpleSpinner.vue";

export default {
    name: "PartContent",

    components: {
        Node,
        SimpleSpinner,
    },

    props: {
        title: {
            type: String,
            required: true,
        },
        part: {
            type: String,
            required: true,
        },
        subpart:{
            type: String,
            required: true
        },
        structure: {
            type: Array,
            required: false,
        },
        resourcesDisplay: {
            type: String,
            required: true,
        },
        headerLinks: {
            type: Boolean,
            required:false,
            default:false
        },
        showResourceButtons: {
            type: Boolean,
            required: false,
            default: true
        },
        supplementalContentCount:{
            type: Object,
            required:false,
            default:() =>{}
        }
    },

    computed: {
        resourcesClass() {
            return `content-with-${this.resourcesDisplay}`;
        },
    },

    methods: {
        emitResourcesParams(scope, identifier) {
            this.$emit("view-resources", {
                scope,
                identifier,
            });
        },
    },
};
</script>

<style lang="scss" scoped>
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$additional-font-path: "~legacy-static/fonts"; // additional Open Sans fonts
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.content-container {
    overflow: auto;
    width: 100%;
    display: flex;
    flex-direction: row;

    .content-with-drawer {
        margin: 0;
    }

    .content-with-sidebar {
        margin-left: 50px;
    }

    .content {
        max-width: $text-max-width;

        article,
        article section {
            padding: 0;
        }

        h1 {
            margin-top: 55px;
            margin-bottom: 40px;
        }
    }
}
.v-application a{
    text-decoration: none;
}
.v-tooltip__content {
    box-shadow: rgba(0, 0, 0, 0.3) 0 2px 10px;
}
.tooltip-text{
    font-size: 12px !important;
    
  
      display: block !important;
  color:#212121;
}
</style>
