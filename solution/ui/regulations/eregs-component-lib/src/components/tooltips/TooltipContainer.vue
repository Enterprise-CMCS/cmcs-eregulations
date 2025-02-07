<template>
    <div class="trigger-btn-container" :class="buttonContainerClasses">
        <button
            class="trigger-btn text-btn"
            :class="buttonClasses"
            :aria-label="ariaLabel"
            @focus="handleEnter"
            @focusout="handleExit"
            @mouseenter="handleEnter"
            @mouseleave="handleExit"
            @click="handleClick"
        >
            <template v-if="btnType === 'link'">
                {{ title }}
            </template>
            <template v-else>
                <i class="fa" :class="faIconType" />
                <span v-if="btnType === 'labeled-icon'">{{ label }}</span>
            </template>
        </button>
        <div
            v-if="hover && entered"
            class="tooltip hovered"
            :class="tooltipClasses"
            :style="tooltipStyles"
        >
            <p class="hover-msg">
                {{ label }}
            </p>
        </div>
        <div
            v-if="click && clicked"
            v-clickaway="handleCloseClick"
            class="tooltip clicked"
            :class="tooltipClasses"
            :style="tooltipStyles"
        >
            <button
                class="close-btn text-btn"
                :aria-label="closeAriaLabel"
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
            <p class="tooltip-title">
                {{ tooltipTitle }}
            </p>
            <slot name="tooltip-content" />
        </div>
    </div>
</template>

<script>
const getAnchorX = (el, elType) => {
    if (!el) return 0;

    return elType === "labeled-icon" || elType === "link"
        ? el.offsetWidth / 2
        : el.offsetWidth * 0.7;
};

const getAnchorY = (el, unused, position) => {
    if (!el) return 0;

    const spacer = position === "over" ? 20 : 10;

    return parseInt(window.getComputedStyle(el).fontSize, 10) + spacer;
};

const appendPxSuffix = (int) => `${int}px`;

const leftWarning = (el) => el.getBoundingClientRect().left < 130;

export default {
    name: "TooltipContainer",

    props: {
        btnClass: {
            type: String,
            default: "copy-btn",
        },
        buttonIcon: {
            type: String,
            default: "link",
        },
        btnType: {
            default: "normal",
            validator: (value) =>
                ["btn", "icon", "labeled-btn", "labeled-icon", "link"].includes(
                    value
                ),
        },
        click: {
            type: Boolean,
            default: false,
        },
        hover: {
            type: Boolean,
            default: false,
        },
        label: {
            type: String,
            required: true,
        },
        position: {
            type: String,
            default: "over",
        },
        title: {
            type: String,
            required: true,
        },
        tooltipTitle: {
            type: String,
            required: true,
        },
    },

    data() {
        return {
            entered: false,
            clicked: false,
            leftSafe: true,
            anchorX: 0,
            anchorY: 0,
        };
    },

    computed: {
        ariaLabel() {
            return this.btnType === "icon"
                ? `${this.label} for ${this.title}`
                : false;
        },
        closeAriaLabel() {
            return `close ${this.label} dialog`;
        },
        buttonClasses() {
            return {
                "trigger-btn-labeled": this.btnType === "labeled-icon",
                "trigger-btn-link": this.btnType === "link",
                [this.btnClass]: true,
            };
        },
        buttonContainerClasses() {
            return {
                [`${this.btnClass}-container`]: true,
            };
        },
        tooltipClasses() {
            return {
                "tooltip-caret": this.leftSafe && this.position === "over",
                "tooltip-caret-top": this.leftSafe && this.position === "under",
                "tooltip-caret-left":
                    !this.leftSafe && this.position === "over",
                "tooltip-caret-top-left":
                    !this.leftSafe && this.position === "under",
            };
        },
        tooltipStyles() {
            if (this.position === "over") {
                return {
                    left: this.anchorX,
                    transform: `translate(-${this.leftSafe ? 50 : 20}%, 0)`,
                    bottom: this.anchorY,
                };
            }

            if (this.position === "under") {
                const spacing = {
                    "margin-top": "10px",
                };

                if (this.leftSafe) {
                    return {
                        transform: `translate(-${this.anchorX}, 0)`,
                        ...spacing,
                    };
                }

                return spacing;
            }

            return {};
        },
        faIconType() {
            return `fa-${this.buttonIcon}`;
        },
    },

    methods: {
        handleEnter(e) {
            this.entered = !this.entered && !this.clicked;
            this.leftSafe = !leftWarning(e.currentTarget);
            this.anchorX = appendPxSuffix(
                getAnchorX(e.currentTarget, this.btnType)
            );
            this.anchorY = appendPxSuffix(
                getAnchorY(this.$el, this.btnType, this.position)
            );
        },
        handleExit() {
            if (!this.clicked) {
                this.entered = false;
                this.anchorX = undefined;
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
                this.anchorX = appendPxSuffix(
                    getAnchorX(e.currentTarget, this.btnType)
                );
                this.anchorY = appendPxSuffix(
                    getAnchorY(this.$el, this.btnType)
                );
            }
        },
        handleCloseClick() {
            if (this.clicked) {
                this.clicked = false;
                this.entered = false;
                this.anchorX = undefined;
                this.leftSafe = true;
                this.selectedAction = null;
            }
        },
    },
};
</script>
