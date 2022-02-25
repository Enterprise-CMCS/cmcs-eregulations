<template>
    <div class="hero-banner">
        <div class="site-container hero-content">
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

export default {
    name: 'Hero',

    components: {
    }
};
</script>

<style></style>
