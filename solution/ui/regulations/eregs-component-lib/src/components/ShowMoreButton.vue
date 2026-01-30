<script setup>
defineProps({
    count: {
        type: Number,
        required: false,
        default: undefined
    },
    buttonText: {
        type: String,
        required: true
    }
});
</script>

<template>
    <div class="show-more-button">
        <b>{{ buttonText }}</b> <span v-if="count" class="show-more-button__count-span">({{ count }})</span>
    </div>
</template>
