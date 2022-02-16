<template>
    <div 
        class="site-title" 
        :class="titleClasses"
    >
        <router-link :to="{ name: 'home' }">
            Medicaid &amp; CHIP eRegulations
        </router-link>
    </div>
</template>

<script>
export default {
    name: "SiteTitle",

    props: {
        part: {
            type: Boolean,
            default: false,
        },
    },

    computed: {
        titleClasses() {
            return {
                "homepage-site-title": !this.part,
            };
        },
    },
};
</script>

<style>
.site-title.homepage-site-title{
    padding:20px 10px;
    border-right:1px #D6D7D9 solid;
}
</style>
