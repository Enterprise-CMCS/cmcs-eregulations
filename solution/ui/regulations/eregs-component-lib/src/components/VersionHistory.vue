<script setup>
import { ref, onMounted } from 'vue';
import { getVersionHistory } from "utilities/api";
import { niceDate } from "utilities/utils";
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
    getVersionHistory({
        apiUrl: props.apiUrl,
        title: props.title,
        part: props.part,
        section: props.section,
    })
        .then((response) => {
            versionHistoryItems.value = response;
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
    <div class="version-history-items__container">
        <div class="version-history__items">
            <SimpleSpinner v-if="loading" size="medium" />
            <div v-else-if="versionHistoryItems.length === 0" class="no-results">
                No results found.
            </div>
            <div v-else class="items__container">
                <div
                    v-for="item in versionHistoryItems"
                    :key="item.id"
                    class="version-history__item"
                >
                    <div class="version-history-item__date">
                        <a
                            :href="item.version_link"
                            class="external bold"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            {{ niceDate(item.version) }}
                        </a>
                    </div>
                    <div
                        v-if="item.compare_to_previous_link || item.compare_to_current_link"
                    >
                        Compare to
                        <span v-if="item.compare_to_previous_link">
                            <a
                                :href="item.compare_to_previous_link"
                                class="external"
                                target="_blank"
                                rel="noopener noreferrer"
                            >Previous Version</a>
                        </span>
                        <span
                            v-if="item.compare_to_previous_link && item.compare_to_current_link"
                        >
                            or
                        </span>
                        <span v-if="item.compare_to_current_link">
                            <a
                                :href="item.compare_to_current_link"
                                class="external"
                                target="_blank"
                                rel="noopener noreferrer"
                            >Current Version</a>

                        </span>
                    </div>
                </div>
            </div>
            <div class="version-history__source">
                Source:
                <a
                    href="https://www.ecfr.gov/reader-aids/using-ecfr/ecfr-changes-through-time"
                    class="external"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    eCFR Point-in-Time System</a>
                (2017–Present)
            </div>
        </div>
    </div>
</template>

<style></style>
