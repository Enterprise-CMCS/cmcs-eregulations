<script setup>
import { ref, onMounted, onUnmounted, useTemplateRef } from "vue";
import eventbus from "../eventbus";
import debounce from "lodash/debounce";
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

const toggleDisplayDynamic = () => {
    if (visible.value && target.value) {
        let desiredHeight;
        if (target.value.children.length === 1) {
            desiredHeight = getFullComputedHeight(target.value.children[0]);
        } else {
            desiredHeight = target.value.scrollHeight;
        }

        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                target.value.style.height = `${desiredHeight}px`;
            });
        });
    }
};

const refreshHeight = ({ name }) => {
    if (dataName.value !== name) {
        return;
    }

    if (props.dynamic && visible.value) {
        toggleDisplayDynamic();
    }
};

const onTransitionEnd = (event) => {
    const eventName = event.target.getAttribute("name");
    const targetName = target.value.getAttribute("name");

    if (eventName !== targetName) {
        return;
    }

    props.dynamic
        ? toggleDisplayDynamic()
        : toggleDisplay();
};

const onResize = () => {
    if (props.dynamic && visible.value) {
        toggleDisplayDynamic();
    }
};

const debouncedOnResize = debounce(onResize, 100);

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
    eventbus.on("refresh-height", refreshHeight);
    window.addEventListener("transitionend", onTransitionEnd);
    window.addEventListener("resize", debouncedOnResize);
});

onUnmounted(() => {
    window.removeEventListener("transitionend", onTransitionEnd);
    window.removeEventListener("resize", debouncedOnResize);
    eventbus.off("refresh-height", refreshHeight);
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
