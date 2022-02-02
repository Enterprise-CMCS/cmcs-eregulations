<template>
    <div class="hero-banner">
        <div class="site-container hero-content">
            <JumpTo />
            <p class="hero-text">
                Explore this site as a supplement to existing policy tools.
                <router-link :to="{ name: 'about', hash: '#automated-updates' }">
                    How this tool is updated.
                </router-link>
            </p>
        </div>
    </div>
</template>

<script>
import JumpTo from "@/components/JumpTo.vue";

export default {
    name: 'Hero',

    components: {
        JumpTo
    }
};
</script>

<style></style>
