<template>
    <v-list class="subpart-list">
        <v-list-item-group class="subpart-list-item-group">
            <v-list-item
                v-for="item in listItems"
                :key="item.identifier"
                @click="clickMethod"
                :data-value="item.identifier"
                class="subpart-list-item"
            >
                <div>
                    <span class="subpart-letter"
                        >Subpart {{ item.identifier }}</span
                    >
                    <span class="subpart-range">{{
                        item.range | formatRange
                    }}</span>
                </div>
                <div class="subpart-text">
                    {{ item.label | descriptionOnly }}
                </div>
            </v-list-item>
        </v-list-item-group>
    </v-list>
</template>

<script>
import _isEmpty from "lodash/isEmpty";

export default {
    name: "SubpartList",

    components: {},

    props: {
        filterEmitter: {
            type: Function,
            required: true,
        },
        listItems: {
            type: Array,
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

    data() {
        return {
            dataProp: "value",
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        clickMethod(e) {
            this.filterEmitter({
                scope: "subpart",
                selectedIdentifier: e.currentTarget.dataset.value,
            });
        },
    },

    filters: {
        descriptionOnly(value) {
            return value.split("-")[1];
        },
        formatRange(array) {
            if (_isEmpty(array)) return "";
            return `(${array.join(" - ")})`;
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

.subpart-list-item {
    display: inline-block;
    min-height: unset;
    padding-top: 5px;
    padding-bottom: 5px;
    font-size: 14px;

    .subpart-letter,
    .subpart-range {
        color: $dark_gray;
    }

    .subpart-range {
        font-size: 12px;
    }

    .subpart-text {
        color: $mid_gray;
    }
}
</style>
