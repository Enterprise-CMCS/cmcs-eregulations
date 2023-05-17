<template>
    <v-list class="title-part-list" role="group">
        <v-list-item
            v-for="item in listItems"
            :key="item.name"
            :data-value="item.name"
            class="title-part-list-item"
            @click="clickMethod"
        >
            <span class="part-number">Part {{ item.name }} - </span>
            <span class="part-text">{{ item.label | descriptionOnly }}</span>
        </v-list-item>
    </v-list>
</template>

<script>
import { getDescriptionOnly } from "utilities/filters";

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
        listId: {
            type: String,
            default: "",
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
            return getDescriptionOnly(value);
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
