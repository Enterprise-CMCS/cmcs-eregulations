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
                        :disabled="value.disabled || value.listItems.length === 0"
                    >
                        <component
                            :is="value.listType"
                            :key="value.buttonId"
                            :filterEmitter="filterEmitter"
                            :listItems=value.listItems
                        ></component>
                    </FancyDropdown>
                </template>
            </div>
        </div>
    </div>
</template>

<script>
import FancyDropdown from "@/components/custom_elements/FancyDropdown.vue";
import TitlePartList from "@/components/custom_elements/TitlePartList.vue";
import SubpartList from "@/components/custom_elements/SubpartList.vue";
import SectionList from "@/components/custom_elements/SectionList.vue";
import CategoryList from "@/components/custom_elements/CategoryList.vue";

export default {
    name: "ResourcesFilters",

    components: {
        FancyDropdown,
        TitlePartList,
        SubpartList,
        SectionList,
        CategoryList,
    },

    props: {
        resourcesDisplay: {
            type: String,
            required: false,
        },
        filters: {
            type: Object,
            required: true,
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

    /*data() {},*/

    computed: {
        resourcesClass() {
            return `content-with-${this.resourcesDisplay}`;
        },
    },

    methods: {
        filterEmitter(payload) {
            console.log(payload)
            this.$emit("select-filter", payload);
        },
    },
};
</script>

<style lang="scss">
.filters-container {
    overflow: auto;
    padding: 0 $spacer-5 30px $spacer-5;
    @include screen-xl {
        padding: 0 $spacer-4 30px $spacer-4;
    }
    .content-with-column {
        margin: 0 auto;
    }
    .content {
        max-width: $text-max-width;
        .filters {
            display: flex;
            justify-content: space-between;
            @include custom-max($mobile-max / 1px) {
                flex-direction: column;
            }
        }
    }
}
</style>
