<template>
    <div class="selections-container">
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
                    @click:close="handleClose(value, name)"
                >
                    {{ value }} {{ name }}
                </v-chip>
            </div>
        </template>
        <v-chip
            v-if="showClearAll"
            class="clear-all-chip"
            outlined
            @click="handleCloseAll"
            >Clear All</v-chip
        >
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

    created() {
        console.log("FilterParams", this.filterParams);
    },

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
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";
.chip-group {
    display: inline;
}
.v-chip.v-chip--outlined.clear-all-chip {
    margin-left: 8px;
    text-transform: uppercase;
    border: none;
    font-size: 12px;
    font-weight: bold;
    color: $mid_blue;
}
</style>
