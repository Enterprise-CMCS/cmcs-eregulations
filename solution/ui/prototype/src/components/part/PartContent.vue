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
            />
        </div>
        <div v-else>
            <SimpleSpinner />
        </div>
    </div>
</template>

<script>
import Node from "@/components/node_types/Node.vue";
import ResourcesBtn from "@/components/ResourcesBtn.vue";
import SimpleSpinner from "legacy/js/src/components/SimpleSpinner.vue";

export default {
    name: "PartContent",

    components: {
        Node,
        ResourcesBtn,
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
        structure: {
            type: Array,
            required: false,
        },
        resourcesDisplay: {
            type: String,
            required: true,
        },
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
        margin: 0 auto;
    }

    .content-with-sidebar {
        margin-left: 50px;
    }

    .content {
        max-width: $text-max-width;

        .btn-container {
            margin: 60px 0 40px;
        }

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
</style>
