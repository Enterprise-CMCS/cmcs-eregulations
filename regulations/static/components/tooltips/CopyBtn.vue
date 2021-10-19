<template>
    <div class="copy-btn-container">
        <button
            class="copy-btn text-btn"
            :class="buttonClasses"
            :aria-label="ariaLabel"
            @focus="handleEnter"
            @focusout="handleExit"
            @mouseenter="handleEnter"
            @mouseleave="handleExit"
            @click="handleClick"
        >
            <i class="fa fa-link"></i>
            <span v-if="btn_type === 'labeled-icon'">{{ label }}</span>
        </button>
        <div
            v-show="entered && btn_type === 'icon'"
            class="copy-tooltip hovered"
            :class="tooltipClasses"
            :style="tooltipStyles"
        >
            <p class="hover-msg">{{ label }}</p>
        </div>
        <div
            v-if="clicked"
            class="copy-tooltip clicked"
            :class="tooltipClasses"
            :style="tooltipStyles"
            v-clickaway="handleCloseClick"
        >
            <button
                class="close-btn text-btn"
                aria-label="close copy link or citation dialog"
                @click="handleCloseClick"
            >
                <svg
                    width="11"
                    height="11"
                    viewBox="0 0 11 11"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        fill-rule="evenodd"
                        clip-rule="evenodd"
                        d="M1.47149 1.08383L5.49969 5.11209L9.52851 1.08383C9.63637 0.975965 9.81124 0.975965 9.91911 1.08383C10.027 1.19169 10.027 1.36656 9.91911 1.47442L5.89023 5.50262L9.91911 9.53144C10.027 9.6393 10.027 9.81417 9.91911 9.92204C9.81124 10.0299 9.63637 10.0299 9.52851 9.92204L5.49969 5.89316L1.47149 9.92204C1.36363 10.0299 1.18876 10.0299 1.0809 9.92204C0.973035 9.81417 0.973035 9.6393 1.0809 9.53144L5.10916 5.50262L1.0809 1.47442C0.973035 1.36656 0.973035 1.19169 1.0809 1.08383C1.18876 0.975965 1.36363 0.975965 1.47149 1.08383Z"
                    />
                </svg>
            </button>
            <p class="citation-title">{{ this.formatted_citation }}</p>
            <div class="action-btns">
                <ActionBtn
                    @action-btn-click="handleActionClick"
                    :selectedAction="selectedAction"
                    :status="copyStatus"
                    actionType="link"
                ></ActionBtn>
                <ActionBtn
                    @action-btn-click="handleActionClick"
                    :selectedAction="selectedAction"
                    :status="copyStatus"
                    actionType="citation"
                ></ActionBtn>
            </div>
        </div>
    </div>
</template>

<script>
import ActionBtn from "./ActionBtn.vue";

const getAnchorY = (el, elType) => {
    if (!el) return 0;

    return elType === "labeled-icon"
        ? el.offsetWidth / 2
        : el.offsetWidth * 0.7;
};

const getAnchorX = (el, elType) => {
    if (!el) return 0;

    return parseInt(window.getComputedStyle(el).fontSize, 10) + 20;
};

const appendPxSuffix = (int) => `${int}px`;

const leftWarning = (el) => el.getBoundingClientRect().left < 130;

export default {
    name: "copy-btn",

    components: {
        ActionBtn,
    },

    props: {
        btn_type: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            required: true,
        },
        hash: {
            type: String,
            required: true,
        },
        formatted_citation: {
            type: String,
            required: true,
        },
    },

    data() {
        return {
            entered: false,
            clicked: false,
            leftSafe: true,
            anchorY: 0,
            anchorX: 0,
            label: "Copy Link or Citation",
            selectedAction: null,
            copyStatus: "idle",
        };
    },

    computed: {
        ariaLabel() {
            return this.btn_type === "icon"
                ? `${this.label} for ${this.title}`
                : false;
        },
        buttonClasses() {
            return {
                "copy-btn-labeled": this.btn_type === "labeled-icon",
            };
        },
        tooltipClasses() {
            return {
                "tooltip-caret": this.leftSafe,
                "tooltip-caret-left": !this.leftSafe,
            };
        },
        tooltipStyles() {
            return {
                left: this.anchorY,
                bottom: this.anchorX,
                transform: `translate(-${this.leftSafe ? 50 : 20}%, 0)`,
            };
        },
    },

    watch: {
        copyStatus: async function (newStatus, oldStatus) {
            if (
                newStatus === "pending" &&
                (oldStatus === "idle" || oldStatus === "success")
            ) {
                try {
                    // async write to clipboard
                    await navigator.clipboard.writeText(this.getCopyText());
                    this.copyStatus = "success";
                } catch (err) {
                    console.log("Error copying to clipboard", err);
                    this.copyStatus = "idle";
                }
            }
        },
    },

    // https://www.vuesnippets.com/posts/click-away/
    // https://dev.to/jamus/clicking-outside-the-box-making-your-vue-app-aware-of-events-outside-its-world-53nh
    directives: {
        clickaway: {
            bind(el, { value }) {
                if (typeof value !== "function") {
                    console.warn(`Expect a function, got ${value}`);
                    return;
                }

                const clickawayHandler = (e) => {
                    const elementsOfInterest = Array.from(
                        el.parentElement.children
                    );
                    const clickedInside = elementsOfInterest.filter((el) =>
                        el.contains(e.target)
                    );
                    return clickedInside.length || value();
                };

                el.__clickawayEventHandler__ = clickawayHandler;

                document.addEventListener("click", clickawayHandler);
            },
            unbind(el) {
                document.removeEventListener(
                    "click",
                    el.__clickawayEventHandler__
                );
            },
        },
    },

    methods: {
        handleEnter(e) {
            this.entered = !this.entered && !this.clicked;
            this.leftSafe = !leftWarning(e.currentTarget);
            this.anchorY = appendPxSuffix(
                getAnchorY(e.currentTarget, this.btn_type)
            );
            this.anchorX = appendPxSuffix(getAnchorX(this.$el, this.btn_type));
        },
        handleExit() {
            if (!this.clicked) {
                this.entered = false;
                this.anchorY = undefined;
                this.leftSafe = true;
            }
        },
        handleClick(e) {
            if (!this.clicked) {
                this.entered = false;
                this.clicked = true;
                if (leftWarning(e.currentTarget)) {
                    this.leftSafe = false;
                }
                this.anchorY = appendPxSuffix(
                    getAnchorY(e.currentTarget, this.btn_type)
                );
                this.anchorX = appendPxSuffix(
                    getAnchorX(this.$el, this.btn_type)
                );
            }
        },
        handleCloseClick() {
            if (this.clicked) {
                this.clicked = false;
                this.entered = false;
                this.anchorY = undefined;
                this.leftSafe = true;
                this.selectedAction = null;
            }
        },
        handleActionClick(payload) {
            this.selectedAction = payload.actionType;
            this.copyStatus = "pending";
        },
        getCopyText() {
            return this.selectedAction === "citation"
                ? this.formatted_citation
                : `${new URL(window.location.href.split("#")[0]).toString()}#${
                      this.hash
                  }`;
        },
    },
};
</script>
