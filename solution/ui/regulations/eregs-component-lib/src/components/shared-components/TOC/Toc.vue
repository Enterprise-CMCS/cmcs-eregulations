<script setup>
import { computed, provide } from "vue";

import TocTitle from "sharedComponents/TOC/TocTitle.vue";
import TocSubheading from "sharedComponents/TOC/TocSubheading.vue";
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

const directChildren = computed(() => {
    return props.structure.children.filter(
        (child) => child.type === "chapter" || child.type === "subtitle"
    )
});

const titleSubheadings = computed(() => {
    return directChildren.value
        ? directChildren.value
            .map(directChild =>`${directChild.label_level} - ${directChild.label_description}`.replace(
                /&amp;/g,
                "&"
            ))
        : undefined
});
</script>

<template>
    <div class="toc__container--inner">
        <TocTitle :title="titleLabel" />
        <template
            v-for="(directChild, i) in directChildren"
            :key="'toc' + i"
        >
            <TocSubheading
                :subheading="titleSubheadings
                    ? titleSubheadings[i]
                    : undefined"
            />
            <TocSubchapter
                v-for="(subchapter, j) in directChild.children"
                :key="'subchapter' + j"
                :subchapter="subchapter"
            />
        </template>
    </div>
</template>
