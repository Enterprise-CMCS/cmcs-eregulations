<template>
    <footer>
        <div class="flexbox">
            <div class="footer-left match-sides">
                <a
                    href="https://www.medicaid.gov/"
                    target="_blank"
                >
                    <img
                        :src="require('legacy-static/images/medicaid.png')"
                        alt="Medicaid.gov logo with subtitle Keeping Agjhmerica Healthy"
                    />
                </a>
                <h5>Centers for Medicare &amp; Medicaid Services</h5>
                <div class="address">
                    7500 Security Boulevard, Baltimore MD 21244
                </div>
                <div class="social">
                    <a
                        href="https://twitter.com/cmsgov"
                        target="_blank"
                        aria-label="CMSgov Twitter page"
                    >
                        <i class="fab fa-twitter fa-2x"></i>
                    </a>
                    <a
                        href="http://www.youtube.com/user/CMSHHSgov"
                        target="_blank"
                        aria-label="CMSgov YouTube page"
                    >
                        <i class="fab fa-youtube fa-2x"></i>
                    </a>
                </div>
            </div>

            <div class="footer-middle match-middle">
                <h4>Legal Limitations of This Tool</h4>
                <p>
                    This tool is a compilation of materials published elsewhere
                    that is made available for convenience. Although we have
                    made efforts to ensure that the material presented is
                    accurate, the rulemaking and regulation information
                    presented on this tool is not an official edition of the
                    <a
                        href="https://www.govinfo.gov/app/collection/cfr"
                        target="_blank"
                        class="external"
                    >
                        Code of Federal Regulations
                    </a>
                    or the
                    <a
                        href="https://federalregister.gov"
                        target="_blank"
                        class="external"
                        aria-label="link to the Federal Register website"
                    >
                        Federal Register
                    </a>
                    , which fully state their own contents. Additional relevant
                    guidance or other interpretive materials may exist.
                </p>
                <br />
                <p>
                    Unless authorized by law to be binding, the guidance linked
                    on this tool does not have the force and effect of law and
                    is not meant to bind CMS or the public in any way, unless
                    specifically incorporated into a contract. The guidance is
                    intended only to provide clarity to the public regarding
                    existing requirements under the law. This tool does not bind
                    CMS or the public and creates no rights, obligations, or
                    defenses, substantive or procedural, that are enforceable by
                    any party in any manner.
                </p>
            </div>

            <div class="footer-right match-sides">
                <h4 class="last-update-footer">
                    Regulations last updated from
                    <a
                        href="https://www.ecfr.gov"
                        target="_blank"
                        class="external"
                    >
                        eCFR
                    </a>
                    on
                    <template v-if="lastUpdated">
                        {{ lastUpdated }}.
                    </template>
                    <template v-else>
                        <InlineLoader />
                    </template>
                </h4>

                <div class="about-footer">
                    <router-link :to="{ name: 'about' }">
                        About Medicaid &amp; CHIP eRegulations
                    </router-link>
                </div>

                <p>
                    A federal government managed website by the Centers for
                    Medicare &amp; Medicaid Services.
                </p>
            </div>
        </div>
    </footer>
</template>

<script>
import { getLastUpdatedDate } from "../utilities/api";
import InlineLoader from "@/components//InlineLoader.vue";

export default {
    name: "Footer",

    components: {
        InlineLoader,
    },

    data() {
        return {
            lastUpdated: "",
        };
    },

    async created() {
        try {
            this.lastUpdated = await getLastUpdatedDate();
        } catch (error) {
            console.error(error);
        }
    },
};
</script>

<style lang="scss">
footer {
    h1,
    h2,
    h3,
    h4,
    h5,
    h6,
    p,
    ul {
        margin-block-start: 0;
        margin-block-end: 0;
    }
}

.social > a {
    margin-right: 5px;
}
</style>
