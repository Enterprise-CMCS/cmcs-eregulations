<template>
    <div class="related-rule recent-change">
        <a
            class="related-rule-title"
            :href="html_url"
            target="_blank"
            rel="noopener noreferrer"
        >
            <span class="link-heading">
                <span :class="getClassList">{{ expandedType }}</span>
                <span v-if="publication_date" class="recent-date">{{
                    publication_date | formatDate
                }}</span>
                | <span class="recent-fr">{{ citation }}</span>
            </span>
            <div class="recent-title">{{ title }}</div>
        </a>
    </div>
</template>

<script>
export default {
    name: "RelatedRule",

    filters: {
        formatDate(value) {
            const date = new Date(value);
            const options = {
                year: "numeric",
                month: "long",
                day: "numeric",
                timeZone: "UTC",
            };
            const format = new Intl.DateTimeFormat("en-US", options);
            return format.format(date);
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
        expandedType() {
            if (this.type === "Rule") {
                return "Final";
            }

            if (
                this.type === "Proposed Rule" &&
                this.action === "Proposed rule."
            ) {
                return "NPRM";
            }

            if (
                this.type === "Proposed Rule" &&
                this.action === "Request for information."
            ) {
                return "RFI";
            }

            return "Unknown";
        },
        getClassList() {
            return this.expandedType === "Final"
                ? "recent-flag indicator"
                : "recent-flag indicator secondary-indicator";
        },
    },

    methods: {},
};
</script>
