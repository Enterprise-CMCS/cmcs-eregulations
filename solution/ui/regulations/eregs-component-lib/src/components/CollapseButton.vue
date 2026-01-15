<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, inject, useTemplateRef } from "vue";
import eventbus from "../eventbus";

const props = defineProps({
    name: {
        type: String,
        required: true,
    },
    state: {
        // expanded or collapsed
        type: String,
        required: true,
    },
    keepContentsOnToggle: {
        type: Boolean,
        required: false,
        default: false,
    },
    discontiguous: {
        type: Boolean,
        required: false,
        default: false,
    },
});

const button = useTemplateRef("button");

const getStateOverride = inject("getStateOverride", null);

const dataName = ref(props.name);
const visible = ref(props.state === "expanded");

const stateOverrideValue = computed(() => {
    if (!getStateOverride) return null;
    return getStateOverride();
});

const click = () => {
    eventbus.emit("collapse-toggle", { name: dataName.value });
};

const toggle = ({ name, action = "toggle" }) => {
    if (dataName.value !== name) return;

    if (props.discontiguous)  button.value.focus();

    if (
        (action === "expand" && visible.value)
        || (action === "collapse" && !visible.value)
    ) return;

    visible.value = !visible.value;
};

watch(stateOverrideValue, (newStateOverrideValue) => {
    if (visible.value && newStateOverrideValue === "collapsed") {
        click();
    } else if (!visible.value && newStateOverrideValue === "expanded") {
        click();
    }
});

onMounted(() => {
    eventbus.on("collapse-toggle", toggle);
});

onBeforeUnmount(() => {
    eventbus.off("collapse-toggle", toggle);
});
</script>

<template>
    <button
        ref="button"
        :class="{ visible: visible }"
        :data-test="dataName"
        :aria-label="visible ? `collapse ${dataName}` : `expand ${dataName}`"
        class="collapsible-title"
        @click="click"
    >
        <slot
            v-if="visible && !keepContentsOnToggle"
            name="expanded"
        >
            Hide
        </slot>
        <slot
            v-if="!visible && !keepContentsOnToggle"
            name="collapsed"
        >
            Show
        </slot>
        <slot v-if="keepContentsOnToggle" name="contents">
            Click here
        </slot>
    </button>
</template>
