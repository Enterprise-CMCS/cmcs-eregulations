<script setup>
import { inject } from "vue";

const aboutUrl = inject("aboutUrl");
const isAuthenticated = inject("isAuthenticated");

const props = defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
});
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
        <a :href="aboutUrl">Learn more about documents on eRegs.</a>
    </div>
</template>

<style></style>
