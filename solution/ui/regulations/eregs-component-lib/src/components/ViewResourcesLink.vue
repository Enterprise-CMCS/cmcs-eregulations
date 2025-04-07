<script setup>
import { defineProps, computed } from 'vue';
import { EventCodes } from "utilities/utils";
import eventbus from "../eventbus";

const props = defineProps({
    section: {
        type: String,
        required: true,
    },
    count: {
        type: String,
        required: true,
    },
    type: {
        type: String,
        required: false,
        default: "link",
    },
});

const clickHandler = () => {
    eventbus.emit(EventCodes.SetSection, {
        section: props.section,
        count: props.count,
    });
};

const isLink = computed(() => props.type === "link");
</script>

<template>
    <div v-if="isLink" class="view-resources-link">
        <button
            v-if="count !== '0'"
            class="link-btn"
            @click="clickHandler"
        >
            <span class="bold">View {{ section }} Resources</span> ({{ count }})
        </button>
        <div v-else class="bold disabled">
            No resources for {{ section }}.
        </div>
    </div>
    <div
        v-else
        class="view-resources-link"
        style="padding-left: 5px"
    >
        <button
            v-if="count !== '0'"
            class="btn default-btn"
            @click="clickHandler"
        >
            <span class="bold">View {{ section }} resources</span>
            <span class="count"> ({{ count }})</span>
        </button>
        <button v-else class="btn disabled">
            <span class="bold">{{ section }} Resources</span>
            <span class="count"> (0)</span>
        </button>
    </div>
</template>
