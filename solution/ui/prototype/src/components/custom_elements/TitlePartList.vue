<template>
    <v-list class="title-part-list">
        <v-list-item-group class="title-part-list-item-group">
            <v-list-item
                v-for="item in listItems"
                :key="item.name"
                @click="clickMethod"
                :data-value="item.name"
                class="title-part-list-item"
            >
                <span class="part-number">Part {{ item.name }} -</span>
                <span class="part-text">{{ item.label | descriptionOnly }}</span>
            </v-list-item>
        </v-list-item-group>
    </v-list>
</template>

<script>
export default {
    name: "TitlePartList",

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

    /*data() {
        return {
            dataProp: "value",
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },*/

    methods: {
        clickMethod(e) {
            this.filterEmitter({
                scope: "part",
                selectedIdentifier: e.currentTarget.dataset.value
            });
        },
    },

    filters: {
        descriptionOnly(value) {
            return value.split("-")[1];
        },
    }
};
</script>

<style lang="scss">
$font-path: "~@cmsgov/design-system/dist/fonts/"; // cmsgov font path
$image-path: "~@cmsgov/design-system/dist/images/"; // cmsgov image path
$fa-font-path: "~@fortawesome/fontawesome-free/webfonts";
$eregs-image-path: "~legacy-static/images";

@import "legacy/css/scss/main.scss";

.title-part-list-item {
    display: inline-block;
    min-height: unset;
    padding-top: 5px;
    padding-bottom: 5px;
    font-size: 15px;

    .part-number {
        color: $dark_gray;
    }

    .part-text {
        color: $mid_gray;
    }
}
</style>
