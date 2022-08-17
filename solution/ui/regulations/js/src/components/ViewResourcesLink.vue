<template>
    <div
        v-if="isLink()"
        style="padding-left: 5px; font-size: 12px; margin-top: -10px"
    >
        <a v-if="this.count !== '0'" v-on:click="clickHandler">
            <span class="bold">View {{ this.section }} resources</span> ({{
                this.count
            }})
        </a>
        <div v-else class="bold disabled">
            No resources for {{ this.section }}.
        </div>
    </div>
    <div v-else style="padding-left: 5px; font-size: 12px">
        <button class="btn" v-if="this.count !== '0'" v-on:click="clickHandler">
            <span class="bold">View {{ this.section }} resources</span> ({{
                this.count
            }})
        </button>
        <button class="btn disabled" v-else>
            <span class="bold">{{ this.section }} Resources</span> (0)
        </button>
    </div>
</template>

<script>
import { EventCodes } from "../../utils";

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
