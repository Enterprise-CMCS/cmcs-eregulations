<script setup>
import { ref, watch} from "vue";
import GovInfoLinks from "./tooltips/GovInfoLinks.vue";
import eventbus from "../eventbus";

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

const visibleRef = ref(false);
const loadedRef = ref(false);
const tab = ref(1);

const handleAnnualEditionsLoaded = ({ name }) => {
    loadedRef.value = true;
    // figure out if parent element is as tall as this element. If not, adjust height of parent.
    eventbus.emit("refresh-height", { name: `${name} section history` });
};

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
        <v-tabs v-model="tab">
            <v-tab
                class="content-tabs"
                tabindex="0"
                disabled
            >
                Version History
            </v-tab>
            <v-tab class="content-tabs" tabindex="0">
                Annual Editions
            </v-tab>
        </v-tabs>
        <v-window v-model="tab">
            <v-window-item />
            <v-window-item>
                <div v-if="!visibleRef" class="rules-container">
                    <p>Loading annual editions...</p>
                </div>
                <template v-else>
                    <GovInfoLinks
                        :api-url="apiUrl"
                        :title="title"
                        :part="part"
                        :section="section"
                        @annual-editions-loaded="handleAnnualEditionsLoaded"
                    />
                </template>
            </v-window-item>
        </v-window>
    </div>
</template>
