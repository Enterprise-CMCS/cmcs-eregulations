<script setup>
import { computed, inject } from "vue";

import { getSubjectNameParts } from "utilities/filters";

const isAuthenticated = inject("isAuthenticated");

const props = defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
});

const subjectsLength = computed(() => props.policyDocSubjects.results.length);
</script>

<template>
    <div class="subj-toc__container">
        <template v-if="props.policyDocSubjects.loading">
            <div class="subj-toc__loading">
                <div class="subj-toc__loading-text">Loading...</div>
            </div>
        </template>
        <template v-else>
            <h1>Browse all {{ subjectsLength }} subjects</h1>
            <ul class="subj-toc__list">
                <li
                    v-for="subject in policyDocSubjects.results"
                    :key="subject.id"
                    class="subj-toc__li"
                    :data-testid="`subject-toc-li-${subject.id}`"
                >
                    <router-link
                        :to="{
                            name: 'subjects',
                            query: {
                                subjects: subject.id.toString(),
                            },
                        }"
                    >
                        <template
                            v-for="(part, index) in getSubjectNameParts(
                                subject
                            )"
                        >
                            <div
                                v-if="part[0]"
                                :key="part[0]"
                                class="subj-toc-li__div"
                                :class="{
                                    'subj-toc-li__abbr': index === 0,
                                    'subjects-toc-li__full-name': index !== 0,
                                    'subj-toc-li__div--bold': part[1],
                                }"
                            >
                                {{ part[0] }}
                            </div>
                        </template>
                    </router-link>
                    <div class="subj-toc-li__count">
                        <span class="subj-doc__count subj-doc__count--public">{{
                            subject.public_resources ?? 0
                        }}</span>
                        public
                        <span v-if="isAuthenticated"
                            >and
                            <span
                                class="subj-doc__count subj-doc__count--internal"
                                >{{ subject.internal_resources ?? 0 }}</span
                            >
                            internal </span
                        >resource<span
                            v-if="
                                isAuthenticated || subject.public_resources != 1
                            "
                            >s</span
                        >
                    </div>
                </li>
            </ul>
        </template>
    </div>
</template>

<style></style>
