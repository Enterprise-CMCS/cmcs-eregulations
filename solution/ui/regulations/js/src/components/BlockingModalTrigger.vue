<template>
    <a tabindex="0" @click="openModal" @keydown.enter.prevent="openModal">
        <span class="trigger-label">{{ triggerLabel }}</span>
    </a>
</template>

<script>
import { EventCodes } from "../../utils";

export default {
    name: "BlockingModalTrigger",

    components: {},

    props: {
        triggerLabel: {
            type: String,
            required: true,
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
            this.$root.$emit(EventCodes.OpenBlockingModal);
        },
    },

}
</script>

<style>

</style>

