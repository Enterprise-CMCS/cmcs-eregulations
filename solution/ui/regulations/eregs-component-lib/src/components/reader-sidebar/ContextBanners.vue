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

const getSectionLink = ({ section }) => `#${section.replace('.', '-')}`;

export default {
    getSectionKeyFromHash,
    getSectionLink,
};
</script>

<script setup>
import { onMounted, onUnmounted, computed } from 'vue';
import { EventCodes, } from "utilities/utils";

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
        default: null,
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

const handleHash = () => {
    const sectionKey = getSectionKeyFromHash({ hash: window.location.hash, part: props.part });
    if (sectionKey) {
        getBanners(sectionKey);
    } else if (props.subparts && props.subparts.length === 1) {
        getBanners()
    }
};

const filteredBanners = computed(() => {
    if (!contextBanners.value.results || contextBanners.value.results.length === 0) return [];
    // If a section is selected, show only that section's banner
    if (props.selectedPart?.value) {
        const sectionText = props.selectedPart.value.replace("§", "").trim(); // e.g., "75.104" or just "104"
        const cleaned = sectionText.split(" ").pop();
        const key = cleaned.includes(".") ? cleaned : `${props.part}.${cleaned}`;
        return contextBanners.value.results.filter((b) => b.section === key);
    }
    // Otherwise, on subpart view, show all banners matching the current subpart
    if (props.subparts && props.subparts.length === 1) {
        const sp = props.subparts[0];
        return contextBanners.value.results.filter((b) => (b.subpart === sp) || !b.subpart);
    }
    return [];
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
    window.addEventListener("hashchange", handleHash);
    handleHash();
    eventbus.on(EventCodes.ClearSections, () => {
        getBanners();
    });
});

onUnmounted(() => {
    window.removeEventListener("hashchange", handleHash);
    eventbus.off(EventCodes.ClearSections);
});
</script>

<template>
    <div
        v-if="filteredBanners.length && !contextBanners.loading"
        class="context-banner"
        role="note"
        aria-label="Context"
    >
        <span class="context-banner-title">Notes</span>
        <p
            v-for="item in filteredBanners"
            :key="item.section"
            class="context-banner__item"
        >
            <template v-if="!props.selectedPart">
                <strong>
                    <a :href="getSectionLink({section: item.section})">§ {{ item.section }}</a>:
                </strong>
                <span v-sanitize-html="item.html" />
            </template>
            <template v-else>
                <span v-sanitize-html="item.html" />
            </template>
        </p>
    </div>
</template>
