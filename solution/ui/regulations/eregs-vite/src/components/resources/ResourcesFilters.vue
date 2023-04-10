<template>
    <div class="filters-container">
        <div class="content content-with-column">
            <h3>Filter Resources</h3>
            <div class="title-filters-chips">
                <div class="title-selector">
                    <FancyDropdown
                        label="Title"
                        list-id="formatListId('Title')"
                        button-title="Select Title"
                        button-id="select-title"
                    >
                    </FancyDropdown>
                </div>
                <div class="filters-and-chips">
                    <div class="filters">
                        <template v-for="(value, name) in filters">
                            <template v-if="name !== 'title'">
                                <FancyDropdown
                                    :key="name"
                                    :label="value.label"
                                    :list-id="formatListId(value.label)"
                                    :button-title="value.buttonTitle"
                                    :button-id="value.buttonId"
                                    :disabled="
                                        value.disabled ||
                                        value.listItems.length === 0
                                    "
                                >
                                    <component
                                        :is="value.listType"
                                        :key="value.buttonId"
                                        :filter-emitter="filterEmitter"
                                        :list-items="value.listItems"
                                        :list-id="formatListId(value.label)"
                                    ></component>
                                </FancyDropdown>
                            </template>
                        </template>
                    </div>
                    <slot name="chips"></slot>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import _camelCase from "lodash/camelCase";

import FancyDropdown from "@/components/custom_elements/FancyDropdown.vue";
import TitleList from "@/components/custom_elements/TitleList.vue";
import PartList from "@/components/custom_elements/PartList.vue";
import SubpartList from "@/components/custom_elements/SubpartList.vue";
import SectionList from "@/components/custom_elements/SectionList.vue";
import CategoryList from "@/components/custom_elements/CategoryList.vue";

export default {
    name: "ResourcesFilters",

    components: {
        FancyDropdown,
        TitleList,
        PartList,
        SubpartList,
        SectionList,
        CategoryList,
    },

    props: {
        filters: {
            type: Object,
            required: true,
        },
    },

    methods: {
        filterEmitter(payload) {
            this.$emit("select-filter", payload);
        },
        formatListId(label) {
            return _camelCase(`${label}List`);
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

        .title-filters-chips {
            display: flex;

            @include custom-max($mobile-max / 1px) {
                flex-direction: column;
            }

            .title-selector {
                background: lightgray;
            }

            .filters-and-chips {
                flex: 1;

                .filters {
                    display: flex;
                    justify-content: space-between;

                    @include custom-max($mobile-max / 1px) {
                        flex-direction: column;
                    }
                }
            }
        }
    }
}
</style>
