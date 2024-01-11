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

    components: {},

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

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

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

