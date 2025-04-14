<script setup>
import { ref, watch, computed } from "vue";
import ActionBtn from "./ActionBtn.vue";

const props = defineProps({
    formattedCitation: {
        type: String,
        required: true,
    },
    hash: {
        type: String,
        required: true,
    },
});

const selectedAction = ref(null);
const copyStatus = ref("idle");

const getCopyText = computed(() => {
    return selectedAction.value === "citation"
        ? props.formattedCitation
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
    <div class="action-btns">
        <ActionBtn
            :selected-action="selectedAction"
            :status="copyStatus"
            action-type="link"
            @action-btn-click="handleActionClick"
        />
        <ActionBtn
            :selected-action="selectedAction"
            :status="copyStatus"
            action-type="citation"
            @action-btn-click="handleActionClick"
        />
    </div>
</template>
