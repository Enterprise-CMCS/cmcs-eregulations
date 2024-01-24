<template>
    <div
        ref="modalElement"
        class="blocking-modal"
        :class="activeClass"
        role="dialog"
        aria-modal="true"
        :aria-label="modalTitle"
    >
        <div class="blocking-modal-content">
            <div class="control-row">
                <button ref="closeBtn" class="close-modal" @click="closeModal">
                    <span class="close-btn-label">Close</span>
                    <svg
                        aria-hidden="true"
                        width="19"
                        height="19"
                        viewBox="0 0 19 19"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <path
                            fill-rule="evenodd"
                            clip-rule="evenodd"
                            d="M1.85355 1.14645L9.14589 8.43889L16.4393 1.14645C16.6346 0.951184 16.9512 0.951184 17.1464 1.14645C17.3417 1.34171 17.3417 1.65829 17.1464 1.85355L9.85289 9.14589L17.1464 16.4393C17.3417 16.6346 17.3417 16.9512 17.1464 17.1464C16.9512 17.3417 16.6346 17.3417 16.4393 17.1464L9.14589 9.85289L1.85355 17.1464C1.65829 17.3417 1.34171 17.3417 1.14645 17.1464C0.951184 16.9512 0.951184 16.6346 1.14645 16.4393L8.43889 9.14589L1.14645 1.85355C0.951184 1.65829 0.951184 1.34171 1.14645 1.14645C1.34171 0.951184 1.65829 0.951184 1.85355 1.14645Z"
                            fill="white"
                            stroke="white"
                            stroke-width="2"
                        />
                    </svg>
                </button>
            </div>
            <slot></slot>
            <div class="bottom-spacer" tabindex="0"></div>
        </div>
    </div>
</template>

<script>
import { EventCodes, trapFocus } from "utilities/utils";
import eventbus from "../eventbus";

export default {
    name: "BlockingModal",

    components: {},

    props: {},

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {
        eventbus.on(EventCodes.OpenBlockingModal, (payload) => {
            this.active = true;
            this.modalTitle = payload.title;
        });
    },

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {
        eventbus.off(EventCodes.OpenBlockingModal);
    },

    destroyed() {},

    data() {
        return {
            active: false,
            modalTitle: "Modal dialog",
            removeFocusTrap: undefined,
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
        closeModal() {
            this.active = false;
        },
    },

    watch: {
        active() {
            document.body.style.overflow = this.active ? "hidden" : "";

            // must remove ariaHidden attribute b/c aria-hidden = "false" can cause issues
            // https://dequeuniversity.com/rules/axe/4.3/aria-hidden-body
            const appContainerEl = document.getElementById("app-container");

            if (this.active) {
                appContainerEl.setAttribute("aria-hidden", "true");
                setTimeout(() => {
                    this.$refs.closeBtn.focus();
                }, 10);
                this.removeFocusTrap = trapFocus(this.$refs.modalElement);
            } else {
                appContainerEl.removeAttribute("aria-hidden");
                this.removeFocusTrap();
                this.removeFocusTrap = undefined;
            }
        },
    },
};
</script>

<style></style>
