<template>
    <div class="filters-container">
        <div class="content" :class="resourcesClass">
            <h3>Filter Resources</h3>
            <div class="filters">
                <template v-for="(value, name) in filters">
                    <FancyDropdown
                        :label="value.label"
                        :buttonTitle="value.buttonTitle"
                        :buttonId="value.buttonId"
                        :key="name"
                    >
                        <TitlePartList :clickMethod="clickMethod" />
                    </FancyDropdown>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
import FancyDropdown from "@/components/FancyDropdown.vue";
import TitlePartList from "@/components/TitlePartList.vue";

export default {
    name: "ResourcesFilters",

    components: {
        FancyDropdown,
        TitlePartList,
    },

    props: {
        resourcesDisplay: {
            type: String,
            required: false,
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            filters: {
                title: {
                    label: "Title",
                    buttonTitle: "Select Title",
                    buttonId: "select-title",
                },
                part: {
                    label: "Part",
                    buttonTitle: "Select Parts",
                    buttonId: "select-parts",
                },
                subpart: {
                    label: "Subpart",
                    buttonTitle: "Select Subparts",
                    buttonId: "select-subparts",
                },
                section: {
                    label: "Section",
                    buttonTitle: "Select Sections",
                    buttonId: "select-sections",
                },
                resourceCategory: {
                    label: "Resource Category",
                    buttonTitle: "Select Categories",
                    buttonId: "select-resource-categories",
                },
            },
        };
    },

    computed: {
        resourcesClass() {
            return `content-with-${this.resourcesDisplay}`;
        },
    },

    methods: {
        clickMethod() {
            this.$emit("select-filter", { payload: "payload" });
        },
    },
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.filters-container {
    overflow: auto;
    width: 100%;

    .content-with-column {
        margin: 0 auto;
    }

    .content-with-sidebar {
        margin-left: 50px;
    }

    .content {
        max-width: $text-max-width;

        .filters {
            display: flex;
            justify-content: space-between;
        }
    }
}
</style>
