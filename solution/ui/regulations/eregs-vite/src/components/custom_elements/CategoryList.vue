<template>
    <v-list class="category-list">
        <v-list-item-group class="category-list-item-group">
            <template v-for="item in listItems">
                <v-list-item
                    :key="item.id"
                    @click="clickMethod"
                    :data-value="item.name"
                    class="category-list-item"
                >
                    <span :class="item.object_type">{{
                        item.name
                    }}</span>
                </v-list-item>
                <v-list-item
                    v-for="subItem in item.subcategories"
                    :key="subItem.id"
                    @click="clickMethod"
                    :data-value="subItem.name"
                    class="category-list-item"
                >
                    <span :class="subItem.object_type">{{
                        subItem.name
                    }}</span>
                </v-list-item>
            </template>
        </v-list-item-group>
    </v-list>
</template>

<script>
export default {
    name: "CategoryList",

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

    methods: {
        clickMethod(e) {
            this.filterEmitter({
                scope: "resourceCategory",
                selectedIdentifier: e.currentTarget.dataset.value,
            });
        },
    },
};
</script>

<style lang="scss">
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
