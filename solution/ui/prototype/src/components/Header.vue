<template>
    <header
        id="header"
        class="sticky"
    >
        <!-- desktop -->
        <div class="flexbox header-large">
            <div class="title-container">
                <SiteTitle />
            </div>
        </div>
    </header>
</template>

<script>
import SiteTitle from "@/components/header/SiteTitle.vue";
import RegTitle from "@/components/header/RegTitle.vue";

export default {
    name: "Header",

    components: {
        SiteTitle,
        RegTitle,
    },
};
</script>

<style></style>
