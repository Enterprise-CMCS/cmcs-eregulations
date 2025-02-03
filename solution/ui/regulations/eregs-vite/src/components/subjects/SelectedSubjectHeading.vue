<script setup>
defineProps({
    selectedSubjectParts: {
        type: Array,
        required: true,
    },
});
</script>

<template>
    <h1>
        <template v-for="(part, index) in selectedSubjectParts">
            <span
                v-if="part[0]"
                :key="part[0]"
                class="subj-heading__span"
                :class="{
                    'subj-heading__span--border': index === 0,
                    'subj-heading__span--bold': part[1],
                }"
            >{{ part[0] }}</span>
        </template>
    </h1>
</template>
