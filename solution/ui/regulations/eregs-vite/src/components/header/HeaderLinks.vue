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

const links = [
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
];

const moreMenuExpanded = ref(false);

const moreClick = () => (moreMenuExpanded.value = !moreMenuExpanded.value);
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
        <button class="more__button" @click="moreClick">
            <!-- chevron up -->
            <svg
                v-if="moreMenuExpanded"
                xmlns="http://www.w3.org/2000/svg"
                width="13"
                height="7"
                viewBox="0 0 13 7"
                fill="none"
            >
                <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M11.8861 6.27859C11.9665 6.19811 12.0053 6.10614 12.0053 6.00267C12.0053 5.89633 11.9665 5.80579 11.8861 5.72531L6.28002 0.119277C6.19955 0.0388007 6.10757 0 6.00267 0C5.8992 0 5.80723 0.0388007 5.72675 0.119277L0.120714 5.72531C0.0416752 5.80579 0 5.89633 0 6.00267C0 6.10614 0.0416752 6.19811 0.120714 6.27859L0.721412 6.87929C0.801889 6.95976 0.895299 7 0.998768 7C1.10367 7 1.19565 6.95976 1.27612 6.87929L6.00267 2.15274L10.7306 6.87929C10.8111 6.95976 10.9031 7 11.008 7C11.1115 7 11.2034 6.95976 11.2839 6.87929L11.8861 6.27859Z"
                    fill="#212121"
                />
            </svg>
            <!-- chevron down -->
            <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                width="13"
                height="7"
                viewBox="0 0 13 7"
                fill="none"
            >
                <path
                    fill-rule="evenodd"
                    clip-rule="evenodd"
                    d="M11.8861 0.721412C11.9665 0.801889 12.0053 0.893862 12.0053 0.997331C12.0053 1.10367 11.9665 1.19421 11.8861 1.27469L6.28002 6.88072C6.19955 6.9612 6.10757 7 6.00267 7C5.8992 7 5.80723 6.9612 5.72675 6.88072L0.120714 1.27469C0.0416752 1.19421 0 1.10367 0 0.997331C0 0.893862 0.0416752 0.801889 0.120714 0.721412L0.721412 0.120714C0.801889 0.0402381 0.895299 0 0.998768 0C1.10367 0 1.19565 0.0402381 1.27612 0.120714L6.00267 4.84726L10.7306 0.120714C10.8111 0.0402381 10.9031 0 11.008 0C11.1115 0 11.2034 0.0402381 11.2839 0.120714L11.8861 0.721412Z"
                    fill="#046791"
                />
            </svg>
            <span>More</span>
        </button>
        <div v-show="moreMenuExpanded" class="more--dropdown-menu">
            <ul class="links__list links__list--dropdown">
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
        </div>
    </div>
</template>
