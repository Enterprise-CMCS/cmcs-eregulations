<script setup>
import { getSubjectName, sortSubjects } from "utilities/filters";

import SubjectChip from "./SubjectChip.vue";

const props = defineProps({
    subjects: {
        type: Array,
        required: true,
    },
});

const sortedSubjects = props.subjects.toSorted(sortSubjects);
</script>

<template>
    <div class="document__subjects">
        <SubjectChip
            v-for="(subject, i) in sortedSubjects"
            :key="subject.id + 'x' + i"
            :subject-id="subject.id"
            :subject-name="getSubjectName(subject)"
        />
    </div>
</template>

<style></style>
