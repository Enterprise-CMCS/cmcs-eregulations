<script setup>
defineProps({
    name: {
        type: String,
        required: true,
    },
    label: {
        type: String,
        required: true,
    },
    active: {
        type: Boolean,
        required: true,
    },
    href: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <a
        :data-testid="name"
        class="header--links__anchor"
        :class="{ active: active }"
        :href="href"
    >
        <span class="anchor__span">{{ label }}</span>
    </a>
</template>
