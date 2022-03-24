<template>
    <v-list class="category-list">
        <v-list-item-group class="category-list-item-group">
            <v-list-item
                v-for="item in listItems"
                :key="item.id"
                @click="clickMethod"
                :data-value="item.name"
                class="category-list-item"
            >
                <span :class="item.object_type">{{
                    item.name
                }}</span>
            </v-list-item>
        </v-list-item-group>
    </v-list>
</template>

<script>
export default {
    name: "CategoryList",

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
                scope: "category",
                selectedIdentifier: e.currentTarget.dataset.value,
            });
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

.category-list-item {
    min-height: unset;
    padding-top: 5px;
    padding-bottom: 5px;
    font-size: 15px;
    color: $dark_gray;

    .subcategory {
        padding-left: 20px;
    }
}
</style>
