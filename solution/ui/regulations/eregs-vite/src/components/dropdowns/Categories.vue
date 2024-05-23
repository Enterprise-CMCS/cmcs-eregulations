<script setup>
import { computed, watch } from "vue";

import { useRoute, useRouter } from "vue-router";

const props = defineProps({
    list: {
        type: Array,
        required: true,
    },
    error: {
        type: Object,
        default: () => {},
    },
    loading: {
        type: Boolean,
        default: true,
    },
});

const $route = useRoute();
const $router = useRouter();

const selectedId = defineModel("id");

const itemProps = (item) => ({
    value: item.id,
    title: item.name,
});

const filteredList = computed(() =>
    props.list.map((item) => ({
        id: item.id,
        name: item.name,
        documentType: "external",
    }))
);

watch(
    () => selectedId.value,
    (newValue) => {
        let categories;

        if (newValue) categories = newValue;

        $router.push({
            name: "subjects",
            query: {
                ...$route.query,
                categories,
            },
        });
    }
);
</script>

<template>
    <v-select
        v-model="selectedId"
        clearable
        label="Choose Category"
        :loading="loading"
        density="compact"
        :items="filteredList"
        :item-props="itemProps"
        variant="outlined"
    ></v-select>
</template>

<style></style>
