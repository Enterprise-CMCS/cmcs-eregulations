<script>
const getButtonTextClasses = (parent) => {
    return {
        "subjects-li__button-text--sidebar": parent === "subjects",
    };
};

const getCount = (subject) => {
    if (subject.count) {
        return subject.count;
    }

    if (subject.public_resources || subject.internal_resources) {
        return (
            (subject.public_resources ?? 0) + (subject.internal_resources ?? 0)
        );
    }

    return "";
};
const getDisplayCount = (subject) => {
    if (getCount(subject)) {
        return `<span class="count">(${getCount(subject)})</span>`;
    }

    return "";
};

export default {
    getButtonTextClasses,
    getCount,
    getDisplayCount,
};
</script>

<script setup>
import { computed, inject } from "vue";

import { getSubjectName, getSubjectNameParts } from "utilities/filters";

defineProps({
    subject: {
        type: Object,
        default: () => ({}),
    },
});

const parent = inject("parent");

const buttonTextClasses = computed(() => getButtonTextClasses(parent));
</script>

<template>
    <span
        v-sanitize-html="
            (subject.displayName || getSubjectName(subject)) +
                getDisplayCount(subject)
        "
        class="subjects-li__button-text"
        :class="buttonTextClasses"
    />
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
    <span
        v-else-if="parent !== 'subjects'"
        v-sanitize-html="
            (subject.displayName || getSubjectName(subject)) +
                getDisplayCount(subject)
        "
        class="subjects-li__button-menu-subtitle"
    />
</template>
