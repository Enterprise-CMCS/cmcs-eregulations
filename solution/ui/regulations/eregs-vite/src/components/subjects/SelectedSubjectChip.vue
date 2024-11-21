<script>
const getCount = (subject) => {
    return (
        subject.count ??
        (subject.public_resources ?? 0) + (subject.internal_resources ?? 0)
    );
};
const getDisplayCount = (subject) => {
    return `<span class="count">(${getCount(subject)})</span>`;
};

export default {
    getDisplayCount,
};
</script>

<script setup>
import { computed, inject } from "vue";

import { getSubjectName, getSubjectNameParts } from "utilities/filters";

const props = defineProps({
    subject: {
        type: Object,
        default: () => ({}),
    },
});

const parent = inject("parent");

const buttonTextClasses = computed(() => ({
    "subjects-li__button-text--sidebar": parent === "subjects",
}));
</script>

<template>
    <span
        class="subjects-li__button-text"
        :class="buttonTextClasses"
        v-html="
            (subject.displayName || getSubjectName(subject)) +
            getDisplayCount(subject)
        "
    ></span>
    <span
        v-if="
            parent === 'subjects' &&
            !subject.displayName &&
            getSubjectNameParts(subject)[0][1]
        "
        class="subjects-li__button-subtitle"
    >
        {{ getSubjectNameParts(subject)[1][0] }}
    </span>
</template>
