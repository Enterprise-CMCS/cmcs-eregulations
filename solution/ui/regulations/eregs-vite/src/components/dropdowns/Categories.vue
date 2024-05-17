<script setup>
import { watch } from "vue";

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

watch(
    () => selectedId.value,
    (newValue, oldValue) => {
        if (!newValue) {
            $router.push({
                name: "subjects",
                query: {
                    ...$route.query,
                    category: null,
                },
            });
        } else {
            $router.push({
                name: "subjects",
                query: {
                    ...$route.query,
                    category: newValue,
                },
            });
        }
    }
);
</script>

<template>
    Selected: {{ selectedId }}
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
