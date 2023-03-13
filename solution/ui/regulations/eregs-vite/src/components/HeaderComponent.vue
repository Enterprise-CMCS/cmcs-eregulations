<script setup>
import { ref, onBeforeMount, onMounted, onUnmounted, onUpdated } from "vue";

defineProps({
    defaultProp: {
        type: String,
        required: false,
        default: "Default string",
    },
});

onMounted(() => {});
</script>

<template>
    <div class="header--brand">
        <a href="/">Medicaid &amp; CHIP eRegulations</a>
    </div>
</template>

<style></style>
