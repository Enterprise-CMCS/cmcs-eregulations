<script setup>
defineProps({
    title: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <div class="nav-container" role="main">
        <div class="content">
            <h1>{{ title }}</h1>
            <slot name="description" />
            <slot name="input" />
            <slot name="filters" />
        </div>
    </div>
</template>
