<template>
    <div
        v-if="filterParams.part || filterParams.resourceCategory"
        class="selections-container"
    >
        <div class="selections-content">
            <template v-for="(array, name, idx) in splitParams">
                <div
                    v-if="array && name !== 'title'"
                    :key="array[0] + name + idx"
                    class="chip-group"
                >
                    <v-chip
                        v-for="value in array"
                        :key="value + name + idx"
                        close
                        close-icon="mdi-close"
                        text-color="#046791"
                        @click:close="handleClose(value, name)"
                    >
                        {{ value | formatChipLabel(name) }}
                    </v-chip>
                </div>
            </template>
            <v-chip
                v-if="showClearAll"
                class="clear-all-chip"
                outlined
                tabindex="0"
                @click="handleCloseAll"
                @keydown.enter.space.prevent="handleCloseAll"
                >Clear All</v-chip
            >
        </div>
    </div>
</template>

<script>
import _isEmpty from "lodash/isEmpty";

export default {
    name: "ResourcesSelections",

    components: {},

    props: {
        filterParams: {
            type: Object,
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
            dataProp: "value",
        };
    },

    computed: {
        showClearAll() {
            const params = { ...this.filterParams };
            delete params.title;
            return !_isEmpty(
                Object.values(params).filter((i) => i !== undefined)
            );
        },
        splitParams() {
            const splitParams = { ...this.filterParams };
            for (const key in splitParams) {
                if (splitParams[key]) {
                    splitParams[key] = splitParams[key].split(",");
                }
            }

            return splitParams;
        },
    },

    methods: {
        handleClose(value, name) {
            this.$emit("chip-filter", {
                scope: name,
                selectedIdentifier: value,
            });
        },
        handleCloseAll() {
            this.$emit("clear-selections");
        },
    },

    filters: {
        formatChipLabel(value, name) {
            switch (name) {
                case "part":
                    return `Part ${value}`;
                    break;
                case "subpart":
                    const part = value.match(/^\d+/)[0];
                    const subpart = value.match(/\w+$/)[0];
                    return `Part ${part} Subpart ${subpart}`;
                    break;
                case "section":
                    return `§ ${value.replace("-", ".")}`;
                    break;
                case "resourceCategory":
                    return `${value}`;
                    break;
                default:
                    return `${name} ${value}`;
            }
        },
    },
};
</script>

<style lang="scss">

@import "legacy/css/scss/main.scss";

.selections-container {
    overflow: auto;
    width: 100%;
    margin-top: 30px;

    .selections-content {
        max-width: $text-max-width;
        margin: 0 auto;

        .chip-group {
            display: inline;
        }

        .v-chip {
            color: $mid_blue;
            font-size: 15px;
            font-weight: 600;
            background: $lightest_blue;
            border: 1px solid #c0eaf8;
            margin-right: 10px;
            margin-bottom: 10px;

            &.v-chip--outlined.clear-all-chip {
                text-transform: uppercase;
                border: none;
                font-size: 12px;
                font-weight: bold;
            }

            .v-chip__content button.v-chip__close {
                color: $mid_blue;
            }
        }
    }
}
</style>
