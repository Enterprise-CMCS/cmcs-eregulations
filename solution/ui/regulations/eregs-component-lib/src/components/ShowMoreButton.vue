<script setup>
defineProps({
    count: {
        type: Number,
        default: 1,
    },
    buttonText: {
        type: String,
        required: true
    }
});
</script>

<template>
    <div class="show-more-button">
        <b>{{ buttonText }}</b> ({{ count }})
    </div>
</template>
