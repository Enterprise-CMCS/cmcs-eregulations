<template>
    <div class="blocking-modal-container" style="display: inline">
        <a tabindex="0" @click="openModal" @keydown.enter.prevent="openModal">
            <span class="trigger-label">{{ triggerLabel }}</span>
        </a>
        <div class="blocking-modal" :class="activeClass">
            <slot></slot>
        </div>
    </div>
</template>

<script>
export default {
    name: "BlockingModal",

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

    data() {
        return {
            active: false,
        };
    },

    computed: {
        activeClass() {
            return {
                active: this.active,
            };
        },
    },

    methods: {
        openModal() {
            this.active = true;
        },
    },
};
</script>

<style></style>
