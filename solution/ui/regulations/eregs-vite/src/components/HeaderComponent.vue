<script setup>
import { ref, onBeforeMount, onMounted, onUnmounted, onUpdated } from "vue";

defineProps({
    defaultProp: {
        type: String,
        required: false,
        default: "Default string",
    },
});

onMounted(() => {});
</script>

<template>
    <div class="header--content-container">
        <div class="header--brand">
            <a href="/">Medicaid &amp; CHIP eRegulations</a>
        </div>
        <div class="header--jump-to">
        </div>
        <div class="header--links-search">
            <div class="header--links">
            </div>
            <div class="header--search">
                <form class="search__form" action="">
                    <input type="search" name="q" placeholder="Search" />
                    <button type="submit" class="search__button--submit" aria-label="Search">
                        <i class="fa fa-search"></i>
                    </button>
                </form>
            </div>
        </div>
    </div>
</template>

<style></style>
