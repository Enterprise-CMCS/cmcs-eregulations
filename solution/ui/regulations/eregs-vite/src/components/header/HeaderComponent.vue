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
    <div class="header--content-container">
        <div class="header--brand">
            <a href="/">Medicaid &amp; <br/>CHIP eRegulations</a>
        </div>
        <div class="header--jump-to">
            <slot name="jump-to"></slot>
        </div>
        <div class="header--links-search">
            <div class="header--links">
                <slot name="links"></slot>
            </div>
            <div class="header--search">
                <slot name="search"></slot>
            </div>
        </div>
    </div>
</template>

<style></style>
