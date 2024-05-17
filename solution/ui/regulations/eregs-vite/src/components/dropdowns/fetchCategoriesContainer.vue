<script setup>
import { computed, inject, ref } from "vue";
import { getCategories } from "utilities/api";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
    filterList: {
        type: Array,
        default: () => [],
    },
});

const apiUrl = inject("apiUrl");

const categoriesList = ref({
    results: [],
    loading: true,
    error: false,
});

// move this fetch pattern to composable
const getCats = async () => {
    categoriesList.value.loading = true;
    categoriesList.value.error = false;

    try {
        categoriesList.value.results = await getCategories(apiUrl, false);
    } catch (error) {
        console.error(error);
        categoriesList.value.error = true;
    } finally {
        categoriesList.value.loading = false;
    }
};

getCats();
</script>

<template>
    <div class="skeleton">
        {{ categoriesList.loading ? "Loading..." : "Loaded" }}
        {{ categoriesList.results }}
    </div>
</template>

<style></style>
