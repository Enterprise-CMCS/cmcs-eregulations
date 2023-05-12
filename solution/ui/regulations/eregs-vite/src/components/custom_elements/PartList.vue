<script setup>
import {
    getDescriptionOnly,
} from "utilities/filters";

const props = defineProps({
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
});

const clickMethod = (e) => {
    this.filterEmitter({
        scope: "part",
        selectedIdentifier: e.currentTarget.dataset.value,
    });
};

</script>

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
            <span class="part-text">{{ getDescriptionOnly(item.label) }}</span>
        </v-list-item>
    </v-list>
</template>

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
