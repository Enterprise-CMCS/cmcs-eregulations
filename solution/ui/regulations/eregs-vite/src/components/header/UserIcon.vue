<script setup>
import { computed, ref } from "vue";

import UserIconSvg from "../svgs/user-icon.vue";

const props = defineProps({
    prop1: {
        type: String,
        required: true,
    },
    prop2: {
        type: Object,
        required: true,
    },
});

const accountClick = () => {
    console.log("account clicked");
};
</script>

<template>
    <button class="user-account__button" @click="accountClick">
        <UserIconSvg />
    </button>
</template>

<style></style>
