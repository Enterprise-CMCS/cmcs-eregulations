<script>
const getSectionKeyFromHash = ({ hash, part }) => {
    if (!hash || hash === "#main-content") return "";
    const trimmed = hash.startsWith("#") ? hash.substring(1) : hash;
    const parts = trimmed.split("-");
    if (parts.length >= 2 && !Number.isNaN(Number(parts[0])) && !Number.isNaN(Number(parts[1]))) {
        return `${part}.${parts[1]}`;
    }
    // Handles hashes like #75.104
    if (trimmed.includes(".")) {
        return trimmed;
    }
    return "";
};

export default {
    getSectionKeyFromHash,
};
</script>

<script setup>
import { computed, onMounted, onUnmounted, watch } from 'vue';
import { EventCodes, } from "utilities/utils";
import CollapseButton from "../CollapseButton.vue";
import Collapsible from "../Collapsible.vue";
import ContextBannerItem from "./ContextBannerItem.vue";
import ShowMoreButton from "../ShowMoreButton.vue";

import useContextBanners from "composables/contextBanners";

import eventbus from "../../eventbus";

const props = defineProps({
    apiUrl: {
        type: String,
        required: false,
        default: "",
    },
    title: {
        type: String,
        required: true,
    },
    part: {
        type: String,
        required: true,
    },
    selectedPart: {
        type: String,
        required: false,
        default: undefined,
    },
    subparts: {
        type: Array,
        required: false,
        default() {
            return [];
        },
    },
});

const { contextBanners, fetchBanners } = useContextBanners();

const filteredBanners = computed(() => {
    if (!contextBanners.value.results || contextBanners.value.results.length === 0) return [[], []];

    if (props.subparts && props.subparts.length === 1) {
        const sp = props.subparts[0];
        const filteredList =  contextBanners.value.results.filter((b) => (b.subpart === sp) || !b.subpart);
        return [filteredList.slice(0,2), filteredList.slice(2)];
    }

    if (props.selectedPart) {
        const sectionText = props.selectedPart.replace("§", "").trim(); // e.g., "75.104" or just "104"
        const cleaned = sectionText.split(" ").pop();
        const key = cleaned.includes(".") ? cleaned : `${props.part}.${cleaned}`;
        const filteredList = contextBanners.value.results.filter((b) => b.section === key);
        return [filteredList.slice(0,2), filteredList.slice(2)];
    }

    const list = contextBanners.value.results;
    return [list.slice(0,2), list.slice(2)];
});

function getBanners(sectionKey) {
    fetchBanners({
        apiUrl: props.apiUrl,
        title: props.title,
        part: props.part,
        sectionKey,
        subparts: props.subparts,
    });
}

onMounted(() => {
    eventbus.on(EventCodes.ClearSections, () => {
        getBanners();
    });
});

onUnmounted(() => {
    eventbus.off(EventCodes.ClearSections);
});

watch(
    () => props.selectedPart,
    (newVal, oldVal) => {
        const sectionKey = getSectionKeyFromHash({ hash: window.location.hash, part: props.part });
        if (newVal && newVal !== oldVal) {
            // Reached when visiting a secion hash
            // while already having a different section in hash
            getBanners(props.selectedPart);
            return;
        }

        if (!newVal && !oldVal && !sectionKey) {
            // Reached on load with no selected part and no section in hash.
            // Should only fire once on initial load due to immediate: true below
            getBanners();
            return;
        }

        if (!newVal && oldVal && !sectionKey) {
            // Reached when clearing selected part and no section in hash.
            // Usually reached by clicked Back button from a hashed section URL
            // to a subpart view without section in hash
            getBanners();
            return;
        }
    },
    { immediate: true }
);
</script>

<template>
    <div
        v-if="filteredBanners[0].length && !contextBanners.loading"
        class="context-banner"
        role="note"
        aria-label="Context"
    >
        <span class="context-banner-title">Notes</span>
        <ContextBannerItem
            v-for="item in filteredBanners[0]"
            :key="item.section"
            :item="item"
            :selected-part="props.selectedPart"
        />
        <template v-if="filteredBanners[1].length">
            <Collapsible
                name="context-banners-collapse"
                state="collapsed"
                class="collapse-content show-more-content"
            >
                <ContextBannerItem
                    v-for="item in filteredBanners[1]"
                    :key="item.section"
                    :item="item"
                    :selected-part="props.selectedPart"
                />
            </Collapsible>
            <CollapseButton
                :class="{ subcategory: subcategory }"
                name="context-banners-collapse"
                state="collapsed"
                class="category-title"
            >
                <template #expanded>
                    <ShowMoreButton button-text="- Show Less" />
                </template>
                <template #collapsed>
                    <ShowMoreButton
                        button-text="+ Show More"
                        :count="filteredBanners[1].length"
                    />
                </template>
            </CollapseButton>
        </template>
    </div>
</template>
