<script setup>
import { ref, onBeforeMount, onMounted, onUnmounted, onUpdated } from "vue";

const defaultLinks = [
    {
        name: "resources",
        label: "Resources",
        active: true,
        link: "link/to/page",
    },
    {
        name: "about",
        label: "About",
        active: false,
        link: "link/to/page",
    },
];

const links = ref(defaultLinks);

onMounted(() => {});
</script>

<template>
    <div class="links--container">
        <ul class="links__list links__list--wide">
            <li v-for="(link, index) in links" :key="index">
                <span
                    class="header--links__anchor"
                    :class="{ active: link.active }"
                >{{ link.label }}</span>
            </li>
        </ul>
        <div class="links__list--trigger-btn">
            More
        </div>
    </div>
</template>
