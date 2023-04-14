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
    selectedTitle: {
        type: String,
        required: false,
        default: undefined,
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
    <ul :id="buttonId" class="title__list">
        <li v-for="title in listItems" :key="title">
            <a
                class="list_item__link"
                :class="{
                    'list_item__link--selected': title == selectedTitle,
                }"
                :data-value="title"
                @click.prevent="clickMethod"
                >Title {{ title }} CFR</a
            >
        </li>
    </ul>
</template>

<style lang="scss">
ul.title__list {
    font-weight: 400;
    list-style: none;
    padding: 0;
    margin: 0;

    li {
        margin-bottom: 4px;

        .list_item__link {
            color: $mid_blue;
            text-decoration: none;

            &--selected {
                color: $dark_blue;
                font-weight: 700;
            }
        }
    }
}
</style>
