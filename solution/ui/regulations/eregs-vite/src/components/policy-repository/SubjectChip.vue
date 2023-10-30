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
        :to="{
            name: 'policy-repository',
            query: {
                subjects: [subjectId.toString()],
            },
        }"
    >
        {{ subjectName }}
    </router-link>
</template>
