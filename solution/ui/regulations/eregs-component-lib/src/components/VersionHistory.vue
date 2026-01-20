<script setup>
import { ref, onMounted } from 'vue';
import { getVersionHistory } from "utilities/api";
import SimpleSpinner from "./SimpleSpinner.vue";

const props = defineProps({
    apiUrl: {
        type: String,
        required: true,
    },
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
});

const emit = defineEmits(["version-history-loaded"]);

const versionHistoryItems = ref([]);
const loading = ref(true);

onMounted(() => {
    console.info("Version History mounted");
    getVersionHistory({
        apiUrl: props.apiUrl,
        title: props.title,
        part: props.part,
        section: props.section,
    })
        .then((response) => {
            versionHistoryItems.value = response.sort((a, b) => b.year - a.year);
        })
        .catch((error) => {
            console.error("Error", error);
            versionHistoryItems.value = [];
        })
        .finally(() => {
            loading.value = false;
            emit("version-history-loaded", { name: `${props.part}.${props.section}` });
        });
});
</script>

<template>
    <div class="version-history-items-container">
        <div class="version-history-items">
            <SimpleSpinner v-if="loading" size="medium" />
            <div v-else-if="versionHistoryItems.length === 0" class="no-results">
                No results found.
            </div>
            <div v-else>
                <div
                    v-for="item in versionHistoryItems"
                    :key="item.id"
                    class="version-history-item"
                >
                    <a
                        :href="item.version_link"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {{ item.version }} Edition
                    </a>
                </div>
            </div>
        </div>
    </div>
</template>

<style></style>
