<template>
    <div class="nav-container" role="main">
        <div class="content">
            <h1>Resources</h1>
            <p>
                Find public documents related to policy research, including
                proposed and final rules published
                <a
                    href="https://www.federalregister.gov/agencies/centers-for-medicare-medicaid-services"
                    target="_blank"
                    class="external"
                    >in the Federal Register</a
                >
                and subregulatory guidance and implementation resources
                published
                <a
                    href="https://www.medicaid.gov/federal-policy-guidance/index.html"
                    target="_blank"
                    class="external"
                    >by CMS</a
                >.
            </p>
            <p>
                <a :href="aboutUrl"
                    >How these links are added and connected to regulation
                    sections.</a
                >
            </p>
            <slot></slot>
        </div>
    </div>
</template>

<script>
export default {
    name: "ResourcesNav",

    props: {
        aboutUrl: {
            type: String,
            default: "/about/",
        },
    },
};
</script>

<style lang="scss">
.nav-container {
    overflow: auto;
    background: $lightest_blue;
    padding: 0 $spacer-5;

    @include screen-xl {
        padding: 0 $spacer-4;
    }

    .content {
        margin: 0 auto;
        max-width: $text-max-width;

        h1 {
            margin-top: 45px;
            margin-bottom: 15px;
        }

        p:last-of-type {
            margin-bottom: 30px;
        }
    }
}
</style>
