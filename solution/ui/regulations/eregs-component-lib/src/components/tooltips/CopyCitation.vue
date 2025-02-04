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

<script>
import ActionBtn from "./ActionBtn.vue";

export default {
    name: "CopyCitation",

    components: {
        ActionBtn,
    },

    props: {
        formattedCitation: {
            type: String,
            required: true,
        },
        hash: {
            type: String,
            required: true,
        },
    },

    data() {
        return {
            selectedAction: null,
            copyStatus: "idle",
        };
    },

    watch: {
        async copyStatus (newStatus, oldStatus) {
            if (
                newStatus === "pending" &&
                (oldStatus === "idle" || oldStatus === "success")
            ) {
                try {
                    // async write to clipboard
                    await navigator.clipboard.writeText(this.getCopyText());
                    this.copyStatus = "success";
                } catch (err) {
                    console.info("Error copying to clipboard", err);
                    this.copyStatus = "idle";
                }
            }
        },
    },

    methods: {
        handleActionClick(payload) {
            this.selectedAction = payload.actionType;
            this.copyStatus = "pending";
        },
        getCopyText() {
            return this.selectedAction === "citation"
                ? this.formattedCitation
                : `${new URL(window.location.href.split("#")[0]).toString()}#${
                    this.hash
                }`;
        },
    },
};
</script>

<style></style>
