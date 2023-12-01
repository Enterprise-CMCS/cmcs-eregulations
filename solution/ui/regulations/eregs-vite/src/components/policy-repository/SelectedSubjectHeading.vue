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
        <span
            v-for="(part, index) in selectedSubjectParts"
            v-if="part[0]"
            :key="part[0]"
            class="subj-heading__span"
            :class="{
                'subj-heading__span--border': index === 0,
                'subj-heading__span--bold': part[1],
            }"
            >{{ part[0] }}</span
        >
    </h1>
</template>
