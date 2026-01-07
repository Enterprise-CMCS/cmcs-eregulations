<script setup>
import { ref, watch} from "vue";
import GovInfoLinks from "./tooltips/GovInfoLinks.vue";

const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    part: {
        type: String,
        required: true,
    },
    section: {
        type: String,
        required: true,
    },
    apiUrl: {
        type: String,
        required: true,
    },
    visible: {
        type: String,
        required: true,
    },
});

const handleAnnualEditionsLoaded = ({ name }) => {
    // Placeholder for any actions needed when annual editions are loaded
    console.info("Annual editions loaded for:", name + " section history");
    // emit eventbus event to refresh collapsible content height?
};

const visibleRef = ref(false);

// Keep the GovInfoLinks component mounted after it becomes visible
watch(
    () => props.visible,
    (newVal, oldVal) => {
        if (!visibleRef.value && !oldVal && newVal) {
            visibleRef.value = true;
        }
    }
);
</script>

<template>
    <div class="version-history-container">
        Tabbed Content Placeholder
        <template v-if="visibleRef">
            <GovInfoLinks
                :api-url="apiUrl"
                :title="title"
                :part="part"
                :section="section"
                @annual-editions-loaded="handleAnnualEditionsLoaded"
            />
        </template>
    </div>
</template>
