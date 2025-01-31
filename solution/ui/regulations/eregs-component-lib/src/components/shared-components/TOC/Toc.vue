<script setup>
import { computed, provide } from "vue";

import TocTitle from "sharedComponents/TOC/TocTitle.vue";
import TocSubchapter from "sharedComponents/TOC/TocSubchapter.vue";

const props = defineProps({
    structure: {
        type: Object,
        required: true,
    },
});

const titleIdentifier = computed(() => props.structure.identifier[0]);

provide("titleIdentifier", titleIdentifier.value);

const titleLabel = computed(() =>
    `${props.structure.label_level} - ${props.structure.label_description}`.replace(
        /&amp;/g,
        "&"
    )
);

const directChild = computed(() =>
    props.structure.children.find(
        (child) => child.type === "chapter" || child.type === "subtitle"
    )
);

const titleSubheading = computed(() =>
    directChild.value
        ? `${directChild.value.label_level} - ${directChild.value.label_description}`.replace(
            /&amp;/g,
            "&"
        )
        : undefined
);
</script>

<template>
    <div class="toc__container--inner">
        <TocTitle :title="titleLabel" :subheading="titleSubheading" />
        <TocSubchapter
            v-for="subchapter in directChild.children"
            :key="subchapter.label_lebel"
            :subchapter="subchapter"
        />
    </div>
</template>
