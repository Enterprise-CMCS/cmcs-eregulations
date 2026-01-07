<script setup>
import { computed, ref, watch} from "vue";

import GovInfoLinks from "./tooltips/GovInfoLinks.vue";

const props = defineProps({
    visible: {
        type: String,
        required: true,
    },
});

const visibleRef = ref(false);

// Keep the GovInfoLinks component mounted after it becomes visible
watch(
    () => props.visible,
    (newVal, oldVal) => {
        if (!oldVal && newVal) {
            visibleRef.value = true;
        }
    }
);
</script>

<template>
    <div class="version-history-container">
        Tabbed Content Placeholder
        <template v-if="visibleRef">
            <slot name="annual-editions" />
        </template>
    </div>
</template>
