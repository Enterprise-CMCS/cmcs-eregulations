<template>
    <div class="related-rule recent-change" :class="ruleClasses">
        <a
            class="related-rule-title"
            :href="html_url"
            target="_blank"
            rel="noopener noreferrer"
        >
            <span class="link-heading">
                <span
                    v-if="type !== ''"
                    class="recent-flag indicator"
                    :class="indicatorClasses"
                >{{type}}</span>
                <span v-if="publication_date" class="recent-date">{{
                    publication_date | formatPubDate
                }}</span>
                |
                <span class="recent-fr-citation" :class="citationClasses">{{
                    citation
                }}</span>
            </span>
            <div v-if="!grouped" class="recent-title">{{ title }}</div>
        </a>
    </div>
</template>

<script>
import { formatDate } from "../../utils";

export default {
    name: "RelatedRule",

    filters: {
        formatPubDate(value) {
            return formatDate(value);
        },
    },

    props: {
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
        publication_date: String,
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
        },
    },

    computed: {
        ruleClasses() {
            return {
                grouped: this.grouped,
                ungrouped: !this.grouped,
            };
        },
        indicatorClasses() {
            return {
                "secondary-indicator":
                    this.grouped || this.type !== "Final",
            };
        },
        citationClasses() {
            return {
                grouped: this.grouped,
            };
        },
    },

    methods: {},
};
</script>
