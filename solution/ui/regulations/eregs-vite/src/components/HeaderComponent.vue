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
    <header id="header" class="sticky">
        <div class="header--brand">
            <a href="/">Medicaid &amp; CHIP eRegulations</a>
        </div>
    </header>
</template>

<style></style>
