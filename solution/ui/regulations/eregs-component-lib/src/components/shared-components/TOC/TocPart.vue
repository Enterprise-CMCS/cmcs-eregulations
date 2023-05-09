<script setup>
import { computed, inject } from "vue";

const props = defineProps({
    part: {
        type: Object,
        required: true,
    },
});

const homeUrl = inject("homeUrl");
const titleIdentifier = inject("titleIdentifier");

const partUrl = computed(() => {
    return `${homeUrl}${titleIdentifier}/${props.part.identifier[0]}`;
});
</script>

<template>
    <div class="toc-part__container">
        <a class="toc-part__anchor" :href="partUrl"
            ><span class="toc-part__label--bold">{{
                props.part.label_level
            }}</span>
            - {{ props.part.label_description }}</a
        >
    </div>
</template>
