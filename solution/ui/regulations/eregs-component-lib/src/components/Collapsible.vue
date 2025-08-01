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

// Accurately measuring height of dynamic content and transitioning smoothly:
// https://dev.to/nikneym/getcomputedstyle-the-good-the-bad-and-the-ugly-parts-1l34
const toggle = (targetName) => {
    if (dataName.value === targetName) {
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
    }
};

onMounted(() => {
    requestAnimationFrame(() => {
        visible.value = props.state === "expanded";
        if (!visible.value && target.value) {
            target.value.classList.add("display-none");
        }
    });
    eventbus.on("collapse-toggle", toggle);
    window.addEventListener("transitionend", toggleDisplay);
});

onUnmounted(() => {
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
