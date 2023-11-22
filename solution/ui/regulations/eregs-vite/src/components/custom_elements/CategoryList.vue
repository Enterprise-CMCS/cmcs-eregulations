<template>
    <v-list class="category-list">
        <template v-for="item in listItems" :key="item.id">
            <v-list-item
                :data-value="item.name"
                class="category-list-item"
                @click="clickMethod"
            >
                <span :class="item.type">{{ item.name }}</span>
            </v-list-item>
            <v-list-item
                v-for="subItem in item.subcategories"
                :key="subItem.id"
                :data-value="subItem.name"
                class="category-list-item"
                @click="clickMethod"
            >
                <span :class="subItem.type">{{ subItem.name }}</span>
            </v-list-item>
        </template>
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
        listId: {
            type: String,
            default: "",
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
