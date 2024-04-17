<template>
    <a tabindex="0" @click="openModal" @keydown.enter.prevent="openModal">
        <span class="trigger-label">{{ triggerLabel }}</span>
    </a>
</template>

<script>
import { EventCodes } from "utilities/utils";
import eventbus from "../eventbus";

export default {
    name: "BlockingModalTrigger",

    props: {
        triggerLabel: {
            type: String,
            required: true,
        },
        modalTitle: {
            type: String,
            default: "Modal dialog",
        },
    },

    methods: {
        openModal() {
            eventbus.emit(EventCodes.OpenBlockingModal, {
                title: this.modalTitle,
            });
        },
    },

}
</script>

<style>

</style>

