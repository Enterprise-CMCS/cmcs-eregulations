<script setup>
import { ref, computed } from 'vue';

// Props
const props = defineProps({
    btnClass: {
        type: String,
        default: "copy-btn",
    },
    buttonIcon: {
        type: String,
        default: "link",
    },
    btnType: {
        type: String,
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
});

// Data (Refs)
const entered = ref(false);
const clicked = ref(false);
const leftSafe = ref(true);
const anchorX = ref(0);
const anchorY = ref(0);

// Computed Properties
const ariaLabel = computed(() => {
    return props.btnType === "icon"
        ? `${props.label} for ${props.title}`
        : false;
});

const closeAriaLabel = computed(() => {
    return `close ${props.label} dialog`;
});

const buttonClasses = computed(() => {
    return {
        "trigger-btn-labeled": props.btnType === "labeled-icon",
        "trigger-btn-link": props.btnType === "link",
        [props.btnClass]: true,
    };
});

const buttonContainerClasses = computed(() => {
    return {
        [`${props.btnClass}-container`]: true,
    };
});

const tooltipClasses = computed(() => {
    return {
        "tooltip-caret": leftSafe.value && props.position === "over",
        "tooltip-caret-top": leftSafe.value && props.position === "under",
        "tooltip-caret-left":
            !leftSafe.value && props.position === "over",
        "tooltip-caret-top-left":
            !leftSafe.value && props.position === "under",
    };
});

const tooltipStyles = computed(() => {
    if (props.position === "over") {
        return {
            left: anchorX.value,
            transform: `translate(-${leftSafe.value ? 50 : 20}%, 0)`,
            bottom: anchorY.value,
        };
    }

    if (props.position === "under") {
        const spacing = {
            "margin-top": "10px",
        };

        if (leftSafe.value) {
            return {
                transform: `translate(-${anchorX.value}, 0)`,
                ...spacing,
            };
        }

        return spacing;
    }

    return {};
});

const faIconType = computed(() => {
    return `fa-${props.buttonIcon}`;
});

// Methods
const getAnchorX = (el, elType) => {
    if (!el) return 0;

    return elType === "labeled-icon" || elType === "link"
        ? el.offsetWidth / 2
        : el.offsetWidth * 0.7;
};

const getAnchorY = (el, _unused, position) => {
    if (!el) return 0;

    const spacer = position === "over" ? 20 : 10;

    return parseInt(window.getComputedStyle(el).fontSize, 10) + spacer;
};

const appendPxSuffix = (int) => `${int}px`;

const leftWarning = (el) => el.getBoundingClientRect().left < 130;

const handleEnter = (e) => {
    entered.value = !entered.value && !clicked.value;
    leftSafe.value = !leftWarning(e.currentTarget);
    anchorX.value = appendPxSuffix(
        getAnchorX(e.currentTarget, props.btnType)
    );
    anchorY.value = appendPxSuffix(
        getAnchorY(e.currentTarget, props.btnType, props.position)
    );
};

const handleExit = () => {
    if (!clicked.value) {
        entered.value = false;
        anchorX.value = undefined;
        leftSafe.value = true;
    }
};

const handleClick = (e) => {
    if (!clicked.value) {
        entered.value = false;
        clicked.value = true;
        if (leftWarning(e.currentTarget)) {
            leftSafe.value = false;
        }
        anchorX.value = appendPxSuffix(
            getAnchorX(e.currentTarget, props.btnType)
        );
        anchorY.value = appendPxSuffix(
            getAnchorY(e.currentTarget, props.btnType)
        );
    }
};

const handleCloseClick = () => {
    if (clicked.value) {
        clicked.value = false;
        entered.value = false;
        anchorX.value = undefined;
        leftSafe.value = true;
    }
};
</script>

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
