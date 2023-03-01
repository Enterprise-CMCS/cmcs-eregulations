<template>
    <div v-if="isLink()" class="view-resources-link">
        <button v-if="count !== '0'" class="link-btn" @click="clickHandler">
            <span class="bold">View {{ section }} Resources</span> ({{ count }})
        </button>
        <div v-else class="bold disabled">No resources for {{ section }}.</div>
    </div>
    <div v-else class="view-resources-link" style="padding-left: 5px">
        <button v-if="count !== '0'" class="btn" @click="clickHandler">
            <span class="bold">View {{ section }} resources</span>
            <span class="count"> ({{ count }})</span>
        </button>
        <button v-else class="btn disabled">
            <span class="bold">{{ section }} Resources</span>
            <span class="count"> (0)</span>
        </button>
    </div>
</template>

<script>
import { EventCodes } from "../utils";

export default {
    name: "ViewResourcesLink",

    props: {
        section: {
            type: Array,
            required: true,
        },
        count: {
            type: Number,
            required: true,
        },
        type: {
            type: String,
            required: false,
            default: "link",
        },
    },
    methods: {
        clickHandler() {
            this.$root.$emit(EventCodes.SetSection, {
                section: this.section,
                count: this.count,
            });
        },
        isLink() {
            return this.type === "link";
        },
    },
};
</script>
