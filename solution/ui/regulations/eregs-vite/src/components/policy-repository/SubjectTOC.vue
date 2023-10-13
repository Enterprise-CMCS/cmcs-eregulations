<script setup>
import { computed, ref } from "vue";
import { getSubjectName } from "utilities/filters";

const props = defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
});
</script>

<template>
    <div class="subjects-toc__container">
        <li
            v-for="subject in policyDocSubjects.results"
            :key="subject.id"
            class="subjects__li sidebar__li"
        >
            <router-link
                :to="{
                    name: 'policy-repository',
                    query: { subjects: subject.id.toString() },
                }"
            >
                <span>{{ subject.abbreviation || subject.full_name }}</span>
                <span v-if="subject.abbreviation">| {{ subject.full_name }}</span>
            </router-link>
        </li>
    </div>
</template>

<style></style>
