<script setup>
import { inject } from "vue";

const base = inject("homeUrl") ?? "/";
const currentRouteName = inject("currentRouteName") ?? "subjects";

defineProps({
    subjectId: {
        type: Number,
        required: true,
    },
    subjectName: {
        type: String,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <a
        v-if="currentRouteName !== 'subjects'"
        class="subject__chip"
        :title="title"
        :data-testid="`add-subject-chip-${subjectId}`"
        :href="`${base}subjects/?subjects=${subjectId}`"
    >
        {{ subjectName }}
    </a>
    <router-link
        v-else
        class="subject__chip"
        :title="title"
        :data-testid="`add-subject-chip-${subjectId}`"
        :to="{
            name: 'subjects',
            query: {
                subjects: subjectId.toString(),
                type: ['all'],
            },
            params: { subjectName },
        }"
    >
        {{ subjectName }}
    </router-link>
</template>
