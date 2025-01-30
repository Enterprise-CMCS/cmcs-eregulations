<script setup>
import { inject } from "vue";
import { useRoute } from "vue-router";

import SignInCTA from "@/components/SignInCTA.vue";
import SignInLink from "@/components/SignInLink.vue";

const aboutUrl = inject("aboutUrl");
const accessUrl = inject("accessUrl");
const customLoginUrl = inject("customLoginUrl");
const homeUrl = inject("homeUrl");
const isAuthenticated = inject("isAuthenticated");

const props = defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
});

const $route = useRoute();
</script>

<template>
    <div class="subj-landing__container">
        <h1>Find Policy Documents</h1>
        <section>
            Use the sidebar to look up policy documents by subject, including:
            <ul>
                <li>Proposed and Final Rules</li>
                <li>Subregulatory Guidance</li>
                <li>Technical Assistance</li>
                <li>OIG and GAO Reports</li>
            </ul>
        </section>
        <section v-if="!isAuthenticated">
            <SignInCTA
                :access-url="accessUrl"
                :is-authenticated="isAuthenticated"
                test-id="loginSubjectsLanding"
            >
                <template #sign-in-link>
                    <SignInLink
                        :custom-login-url="customLoginUrl"
                        :home-url="homeUrl"
                        :is-authenticated="isAuthenticated"
                        :route="$route"
                    />
                </template>
            </SignInCTA>
        </section>
        <a
            class="about__anchor"
            :href="aboutUrl"
        >Learn more about documents on eRegs.</a>
    </div>
</template>

<style></style>
