<script setup>
import CategoriesItem from "./CategoriesItem.vue";

const itemTypes = { CategoriesItem };

defineProps({
    itemType: {
        type: String,
        default: undefined,
    },
});
</script>

<template>
    <v-select
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
            <component
                :is="itemTypes[itemType]"
                :scoped-props="props"
                :item="item"
            />
        </template>
    </v-select>
</template>

<style></style>
