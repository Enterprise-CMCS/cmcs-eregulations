<script setup>
import { computed, ref } from "vue";

const props = defineProps({
    name: {
        type: String,
        required: true,
    },
    type: {
        type: String,
        default: "category",
    },
});

console.log("name", props.name);

const labelClass = computed(() => {
    return props.type === "subcategory"
        ? "subcategory-label"
        : "category-label";
});
</script>

<template>
    <div
        class="result-label"
        :class="labelClass"
    >
        {{ name }}
    </div>
</template>

<style></style>
