<script setup>
import CategoriesItem from "./CategoriesItem.vue";

const itemTypes = { CategoriesItem };

const props = defineProps({
    itemType: {
        type: String,
        default: undefined,
    },
});
</script>

<template>
    <v-select
        menu
        class="filter__select"
        variant="outlined"
        clearable
        persistent-clear
        single-line
        hide-details
        flat
        clear-icon="mdi-close"
        menu-icon="mdi-menu-swap"
        density="compact"
    >
        <template v-if="itemType" #item="{ props, item }">
            <v-list-item v-bind="props">
                <component :is="itemTypes[itemType]" :item="item" />
            </v-list-item>
        </template>
    </v-select>
</template>

<style></style>
