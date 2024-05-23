<script setup>
import { watch } from "vue";

import { useRoute, useRouter } from "vue-router";

defineProps({
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

watch(
    () => selectedId.value,
    (newValue) => {
        if (!newValue) {
            $router.push({
                name: "subjects",
                query: {
                    ...$route.query,
                    categories: undefined,
                },
            });
        } else {
            $router.push({
                name: "subjects",
                query: {
                    ...$route.query,
                    categories: newValue,
                },
            });
        }
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
        :items="list"
        item-title="name"
        item-value="id"
        variant="outlined"
    ></v-select>
</template>

<style></style>
