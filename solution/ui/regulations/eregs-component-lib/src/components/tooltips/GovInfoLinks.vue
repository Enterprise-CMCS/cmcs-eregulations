<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { getGovInfoLinks } from "utilities/api";
import SimpleSpinner from "../SimpleSpinner.vue";
import eventbus from "../../eventbus";

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

const govInfoLinks = ref([]);
const loading = ref(true);

const handleScrollTriggerVisible = ({ trigger }) => {
    if (trigger === `${props.part}.${props.section}`) {
        getGovInfoLinks({
            apiUrl: props.apiUrl,
            filterParams: {
                title: props.title,
                part: props.part,
                section: props.section,
            },
        })
            .then((response) => {
                govInfoLinks.value = response.sort((a, b) => b.year - a.year);
            })
            .catch((error) => {
                console.error("Error", error);
                govInfoLinks.value = [];
            })
            .finally(() => {
                loading.value = false;
            });
    }
};

onMounted(() => {
    eventbus.on("scroll-trigger-visible", handleScrollTriggerVisible);
});

onUnmounted(() => {
    eventbus.off("scroll-trigger-visible", handleScrollTriggerVisible);
});
</script>

<template>
    <div class="gov-info-links-container">
        <div class="gov-info-links">
            <SimpleSpinner v-if="loading" size="medium" />
            <div v-else-if="govInfoLinks.length === 0" class="no-results">
                No results found.
            </div>
            <div v-else class="links-container">
                <a
                    v-for="(yearObj, index) in govInfoLinks"
                    :key="index"
                    :href="yearObj.link"
                    class="external"
                    target="_blank"
                    rel="noopener noreferrer"
                >{{ yearObj.year }}</a>
            </div>
        </div>
        <div class="gov-info-source">
            Source: CFR Annual Edition from
            <a
                href="https://www.govinfo.gov/app/collection/cfr"
                class="external"
                target="_blank"
                rel="noopener noreferrer"
            >
                GovInfo</a>
            (1996–Present)
        </div>
    </div>
</template>


