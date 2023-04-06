<script setup>
const props = defineProps({
    filterEmitter: {
        type: Function,
        required: true,
    },
    listItems: {
        type: Array,
        required: true,
    },
});

const clickMethod = (e) => {
    props.filterEmitter({
        scope: "title",
        selectedIdentifier: e.currentTarget.dataset.value,
    });
};
</script>

<template>
    <v-list class="title-list" role="group">
        <v-list-item
            v-for="item in props.listItems"
            :key="item"
            :data-value="item"
            class="title-list-item"
            @click="clickMethod"
        >
            {{ item }}
        </v-list-item>
    </v-list>
</template>

<style lang="scss">
.title-list-item {
    display: block;
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
