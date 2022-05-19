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
                scope: "part",
                selectedIdentifier: e.currentTarget.dataset.value,
            });
        },
    },

    filters: {
        descriptionOnly(value) {
            return value.substring(value.indexOf("-") + 1);
        },
    },
};
</script>

<style lang="scss">
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
