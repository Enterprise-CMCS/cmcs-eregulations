<script setup>
import { getSubjectName } from "utilities/filters";

import SubjectChip from "./SubjectChip.vue";

const props = defineProps({
    subjects: {
        type: Array,
        required: true,
    },
});

</script>

<template>
    <div class="document__subjects">
        <SubjectChip
            v-for="(subject, i) in subjects"
            :key="subject.id + 'x' + i"
            :subject-id="subject.id"
            :subject-name="getSubjectName(subject)"
            :title="subject.full_name"
        />
    </div>
</template>

<style></style>
