<template>
    <div class="latest-changes">
        <h3>Recent Documents for 42 CFR 430-460</h3>

        <RelatedRules
            class="related-rules"
            title="42"
            part="430-460"
        />

        <p class="see-fr">
            For more changes, see the
            <a
                href="https://www.federalregister.gov/"
                target="_blank"
                class="external"
            >Federal Register</a>.
        </p>
    </div>
</template>

<script>
import RelatedRules from "legacy/eregs-component-lib/src/components/RelatedRules.vue";

export default {
    name: "RecentChanges",

    components: {
        RelatedRules,
    },
};
</script>

<style></style>
