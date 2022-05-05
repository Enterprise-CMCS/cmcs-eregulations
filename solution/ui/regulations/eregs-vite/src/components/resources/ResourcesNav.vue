<template>
    <div class="nav-container">
        <div class="content">
            <h1>Resources</h1>
            <p class="descriptive-text">
                Resources are curated and updated by a Medicaid subject matter
                expert. Final Rules, NPRMs, and RFIs  are automatically pulled
                from the
                <a href="https://www.federalregister.gov/" target="_blank"
                    >Federal Register</a
                >.
            </p>
            <slot></slot>
        </div>
    </div>
</template>

<script>

export default {
    name: "ResourcesNav",

    components: {},

    props: {},

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    computed: {},

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style lang="scss">
.nav-container {
    overflow: auto;
    width: 100%;
    background: $lightest_blue;

    .content {
        margin: 0 auto;
        max-width: $text-max-width;

        h1 {
            margin-top: 45px;
            margin-bottom: 15px;
        }

        p.descriptive-text {
            margin-bottom: 30px;
        }

        a::after {
            @include external-link;
        }
    }
}
</style>
