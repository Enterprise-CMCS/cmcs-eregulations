<script setup>
import { ref, watch, computed } from "vue";
import ActionBtn from "./ActionBtn.vue";

const props = defineProps({
    formattedCitation: {
        type: String,
        required: false,
        default: undefined,
    },
    hash: {
        type: String,
        required: false,
        default: undefined,
    },
    link: {
        type: String,
        required: false,
        default: undefined,
    },
    actionType: {
        type: String,
        required: false,
        default: undefined,
    },
});

const selectedAction = ref(null);
const copyStatus = ref("idle");

const POSSIBLE_ACTIONS = ["link", "citation"];
const actions = computed(() => {
    if (POSSIBLE_ACTIONS.includes(props.actionType)) {
        return [props.actionType];
    }

    return POSSIBLE_ACTIONS;
})

const getCopyText = computed(() => {
    return selectedAction.value === "citation"
        ? props.formattedCitation
        : props.link
            ? props.link
            : `${new URL(window.location.href.split("#")[0]).toString()}#${props.hash}`;
});

const handleActionClick = (payload) => {
    selectedAction.value = payload.actionType;
    copyStatus.value = "pending";
};

watch(
    copyStatus,
    async (newStatus, oldStatus) => {
        if (
            newStatus === "pending" &&
      (oldStatus === "idle" || oldStatus === "success")
        ) {
            try {
                await navigator.clipboard.writeText(getCopyText.value);
                copyStatus.value = "success";
            } catch (err) {
                console.info("Error copying to clipboard", err);
                copyStatus.value = "idle";
            }
        }
    }
);
</script>

<template>
    <ActionBtn
        v-for="action in actions"
        :key="action"
        :selected-action="selectedAction"
        status="idle"
        :action-type="action"
        @action-btn-click="handleActionClick"
    />
</template>
