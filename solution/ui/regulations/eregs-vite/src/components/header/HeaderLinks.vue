<script setup>
import { ref, onBeforeMount, onMounted, onUnmounted, onUpdated } from "vue";

const props = defineProps({
    aboutUrl: {
        type: String,
        required: true,
    },
    resourcesUrl: {
        type: String,
        required: true,
    },
});

const links = ref([
    {
        name: "resources",
        label: "Resources",
        active: window.location.pathname.includes("resources"),
        href: props.resourcesUrl,
    },
    {
        name: "about",
        label: "About",
        active: window.location.pathname.includes("about"),
        href: props.aboutUrl,
    },
]);

onMounted(() => {});
</script>

<template>
    <div class="links--container">
        <ul class="links__list links__list--wide">
            <li v-for="(link, index) in links" :key="index">
                <a
                    class="header--links__anchor"
                    :class="{ active: link.active }"
                    :href="link.href"
                >
                    <span class="anchor__span">{{ link.label }}</span>
                </a>
            </li>
        </ul>
        <div class="links__list--trigger-btn">More</div>
    </div>
</template>
