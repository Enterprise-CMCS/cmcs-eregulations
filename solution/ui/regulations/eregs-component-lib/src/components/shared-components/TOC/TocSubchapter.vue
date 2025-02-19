<script setup>
import TocPart from "sharedComponents/TOC/TocPart.vue";

defineProps({
    subchapter: {
        type: Object,
        required: true,
    },
});
</script>

<template>
    <div class="toc-subchapter__container">
        <h4 class="toc-subchapter__label">
            {{ subchapter.label_level }} - {{ subchapter.label_description }}
        </h4>
        <TocPart
            v-for="part in subchapter.children"
            :key="part.label_level"
            :part="part"
        />
    </div>
</template>
