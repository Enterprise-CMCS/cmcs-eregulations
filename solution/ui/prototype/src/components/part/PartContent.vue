<template>
    <div class="content-container">
        <div v-if="structure" class="content reg-text">
            <v-btn color="primary" outlined @click="handleBtnClick">
                View Part Resources
            </v-btn>
            <template v-for="item in structure">
                <Node
                    :node="item"
                    :key="item.title"
                    :resourceParamsEmitter="emitResourcesParams"
                />
            </template>
        </div>
        <div v-else>
            <SimpleSpinner />
        </div>
    </div>
</template>

<script>
import Node from "@/components/node_types/Node.vue";
import SimpleSpinner from "legacy/js/src/components/SimpleSpinner.vue";

export default {
    name: "PartContent",

    components: {
        Node,
        SimpleSpinner,
    },

    props: {
        part: {
            type: String,
            required: true,
        },
        structure: {
            type: Array,
            required: false,
        },
    },

    methods: {
        emitResourcesParams(scope, identifier) {
            this.$emit("view-resources", {
                scope,
                identifier,
            });
        },
        handleBtnClick() {
            this.emitResourcesParams("part", this.part);
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

    .content {
        max-width: $text-max-width;
        margin: 0 auto;

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
