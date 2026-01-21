<script setup>
import { ref, watch} from "vue";
import GovInfoLinks from "./GovInfoLinks.vue";
import VersionHistory from "./VersionHistory.vue";
import eventbus from "../eventbus";
import debounce from "lodash/debounce";

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
const tab = ref(0);

const handleLoaded = ({ name }) => {
    loadedRef.value = true;
    eventbus.emit("refresh-height", { name: `${name} section history` });
};

const onTransitionEnd = () => {
    eventbus.emit("refresh-height", { name: `${props.part}.${props.section} section history` });
};

const debouncedOnTransitionEnd = debounce(onTransitionEnd, 100);

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
    <div class="version-history__container">
        <v-tabs v-model="tab">
            <v-tab
                class="content-tabs"
                tabindex="0"
                data-testid="version-history-tab"
            >
                Version History
            </v-tab>
            <v-tab
                class="content-tabs"
                tabindex="0"
                data-testid="annual-editions-tab"
            >
                Annual Editions
            </v-tab>
        </v-tabs>
        <v-window v-model="tab">
            <v-window-item @transitionend="debouncedOnTransitionEnd">
                <div v-if="!visibleRef" class="rules-container">
                    <p>Loading version history...</p>
                </div>
                <template v-else>
                    <VersionHistory
                        :api-url="apiUrl"
                        :title="title"
                        :part="part"
                        :section="section"
                        @version-history-loaded="handleLoaded"
                    />
                </template>
            </v-window-item>
            <v-window-item @transitionend="debouncedOnTransitionEnd">
                <div v-if="!visibleRef" class="rules-container">
                    <p>Loading annual editions...</p>
                </div>
                <template v-else>
                    <GovInfoLinks
                        :api-url="apiUrl"
                        :title="title"
                        :part="part"
                        :section="section"
                        @annual-editions-loaded="handleLoaded"
                    />
                </template>
            </v-window-item>
        </v-window>
    </div>
</template>
