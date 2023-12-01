<script setup>
const props = defineProps({
    selectedSubjectParts: {
        type: Array,
        required: true,
    },
});
</script>

<template>
    <h1>
        <div
            v-for="(part, index) in props.selectedSubjectParts"
            v-if="part[0]"
            :key="part[0]"
            :class="{ bold: part[1] }"
        >
            {{ part[0] }}
        </div>
    </h1>
</template>
