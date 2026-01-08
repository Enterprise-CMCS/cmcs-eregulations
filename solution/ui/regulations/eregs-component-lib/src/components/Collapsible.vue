<script setup>
import { ref, onMounted, onUnmounted, useTemplateRef } from "vue";
import eventbus from "../eventbus";
import { getFullComputedHeight } from "utilities/utils";

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
    dynamic: {
        type: Boolean,
        required: false,
        default: false,
    },
});

const target = useTemplateRef("target");
const dataName = ref(props.name);
const visible = ref(false);
const styles = {
    transition: props.transition,
    overflow: "hidden",
};

const toggleDisplay = (event) => {
    const eventName = event.target.getAttribute("name");
    const targetName = target.value.getAttribute("name");

    if (eventName !== targetName) {
        return;
    }

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

const toggleDisplayDynamic = (event) => {
    const eventName = event.target.getAttribute("name");
    const targetName = target.value.getAttribute("name");

    if (eventName !== targetName) {
        return;
    }

    if (visible.value) {
        if (target.value) {
            const targetHeight = getFullComputedHeight(target.value.children[0]) + "px";
            target.value.style.height = targetHeight;
        }
    }
};

const onTransitionEnd = (event) => {
    if (props.dynamic) {
        toggleDisplayDynamic(event);
    } else {
        toggleDisplay(event);
    }
};

// Accurately measuring height of dynamic content and transitioning smoothly:
// https://dev.to/nikneym/getcomputedstyle-the-good-the-bad-and-the-ugly-parts-1l34
const toggle = ({ name, action = "toggle" }) => {
    if (
        dataName.value !== name
        || (action === "expand" && visible.value)
        || (action === "collapse" && !visible.value)
    ) {
        return;
    }

    if (!visible.value && target.value) {
        target.value.classList.remove("display-none");
        target.value.style.overflow = "hidden";
        target.value.classList.remove("invisible");
    }

    target.value.style.height = "auto";

    const height = getComputedStyle(target.value).height;

    if (!visible.value && target.value) {
        target.value.style.height = "0px";
    } else if (target.value) {
        target.value.style.height = "";
    }

    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            target.value.style.height = height;
            requestAnimationFrame(() => {
                visible.value = !visible.value;
            });
        });
    });
};

onMounted(() => {
    requestAnimationFrame(() => {
        visible.value = props.state === "expanded";
        if (!visible.value && target.value) {
            target.value.classList.add("display-none");
        }
    });
    eventbus.on("collapse-toggle", toggle);
    window.addEventListener("transitionend", onTransitionEnd);
});

onUnmounted(() => {
    window.removeEventListener("transitionend", onTransitionEnd);
    eventbus.off("collapse-toggle", toggle);
});
</script>

<template>
    <div
        ref="target"
        :name="dataName"
        :data-test="dataName"
        :class="{ invisible: !visible }"
        :style="[styles]"
    >
        <slot
            :visible="visible"
        />
    </div>
</template>
