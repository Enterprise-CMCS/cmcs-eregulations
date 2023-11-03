<script setup>
const props = defineProps({
    subjectId: {
        type: Number,
        required: true,
    },
    subjectName: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <router-link
        class="subject__chip"
        :data-testid="`add-subject-chip-${subjectId}`"
        :to="{
            name: 'policy-repository',
            query: {
                subjects: [subjectId.toString()],
                type: ['all'],
            },
        }"
    >
        {{ subjectName }}
    </router-link>
</template>
