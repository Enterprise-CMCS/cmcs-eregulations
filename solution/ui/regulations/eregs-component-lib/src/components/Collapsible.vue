<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import eventbus from "../eventbus";

const props = defineProps({
    name: {
        type: String,
        required: true,
    },
    state: {
        //expanded or collapsed
        type: String,
        required: true,
    },
    transition: {
        type: String,
        required: false,
        default: "0.5s",
    },
    overflow: {
        type: Boolean,
        required: false,
        default: false,
    },
});

const target = ref(null);
const dataName = ref(props.name);
const height = ref("auto");
const visible = ref(false);
const styles = {
    transition: props.transition,
    overflow: "hidden",
};

const resize = () => {
    computeHeight();
};

const toggleDisplay = () => {
    if (visible.value) {
        if (target.value) {
            target.value.style.height = "auto";
            if (props.state === "collapsed" && props.overflow) {
                target.value.style.overflow = "visible";
            }
        }
    } else if (target.value) {
        target.value.classList.add("display-none");
        target.value.style.overflow = "hidden";
    }
};

const toggle = (targetName) => {
    if (dataName.value === targetName) {
        if (target.value) {
            target.value.classList.remove("display-none");
            target.value.style.overflow = "hidden";
        }
        requestAnimationFrame(() => {
            computeHeight();
            requestAnimationFrame(() => {
                visible.value = !visible.value;
            });
        });
    }
};

const getStyle = () => {
    if (target.value) {
        return window.getComputedStyle(target.value);
    }
    return "auto";
};

const setProps = (visibility, display, position, heightValue) => {
    if (target.value) {
        target.value.style.visibility = visibility;
        target.value.style.display = display;
        target.value.style.position = position;
        target.value.style.height = heightValue;
    }
};

const computeHeightInternal = () => {
    if (getStyle().display === "none") {
        return "auto";
    }

    if (target.value) {
        target.value.classList.remove("invisible");
        setProps("hidden", "block", "absolute", "auto");
    }

    const heightValue = getStyle().height;

    if (target.value) {
        setProps(null, null, null, heightValue);
    }

    if (!visible.value && target.value) {
        target.value.classList.add("invisible");
    }
    return heightValue;
};

const computeHeight = () => {
    height.value = computeHeightInternal();
};

onMounted(() => {
    requestAnimationFrame(() => {
        visible.value = props.state === "expanded";
        if (!visible.value && target.value) {
            target.value.classList.add("display-none");
        }
    });
    eventbus.on("collapse-toggle", toggle);
    window.addEventListener("resize", resize);
    window.addEventListener("transitionend", toggleDisplay);
});

onUnmounted(() => {
    window.removeEventListener("resize", resize);
    window.removeEventListener("transitionend", toggleDisplay);
    eventbus.off("collapse-toggle", toggle);
});
</script>

<template>
    <div
        ref="target"
        :data-test="dataName"
        :class="{ invisible: !visible }"
        :style="[styles]"
    >
        <slot />
    </div>
</template>
