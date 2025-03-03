<script setup>
/* eslint-disable vue/prop-name-casing */
import { computed, inject } from "vue";

import { formatDate } from "utilities/utils";

import IndicatorLabel from "./shared-components/results-item-parts/IndicatorLabel.vue";

const props = defineProps({
    title: {
        type: String,
        required: true,
    },
    type: {
        type: String,
        required: true,
    },
    grouped: {
        type: Boolean,
        required: false,
        default: false,
    },
    citation: {
        type: String,
        required: true,
    },
    publication_date: {
        type: String,
        default: undefined,
    },
    document_number: {
        type: String,
        required: true,
    },
    html_url: {
        type: String,
        required: true,
    },
    action: {
        type: String,
        default: undefined,
    },
});

const isBlank = (str) => {
    return !str || /^\s*$/.test(str);
};

const itemTitleLineLimit = inject("itemTitleLineLimit", { default: 9 });

const formatPubDate = (value) => {
    return formatDate(value);
};

const ruleClasses = computed(() => {
    return {
        grouped: props.grouped,
        ungrouped: !props.grouped,
    };
});

const citationClasses = computed(() => {
    return {
        grouped: props.grouped,
    };
});

const recentTitleClass = computed(() => {
    return `line-clamp-${itemTitleLineLimit}`;
});

</script>

<template>
    <div class="related-rule recent-change" :class="ruleClasses">
        <a
            class="related-rule-title"
            :href="html_url"
            target="_blank"
            rel="noopener noreferrer"
        >
            <span class="link-heading">
                <IndicatorLabel v-if="type" :type="type" />
                <span
                    v-if="publication_date"
                    class="recent-date"
                    :class="{
                        'recent-date--bar': !isBlank(citation),
                    }"
                >{{
                    formatPubDate(publication_date)
                }}</span>
                <span class="recent-fr-citation" :class="citationClasses">{{
                    citation
                }}</span>
            </span>
            <div
                v-if="!grouped"
                class="recent-title"
                :class="recentTitleClass"
            >
                {{ title }}
            </div>
        </a>
    </div>
</template>
