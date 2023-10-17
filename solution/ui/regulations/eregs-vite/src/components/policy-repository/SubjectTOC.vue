<script setup>
import { computed, ref } from "vue";

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
                >
                    <router-link
                        :to="{
                            name: 'policy-repository',
                            query: { subjects: subject.id.toString() },
                        }"
                    >
                        <div
                            v-if="subject.abbreviation || subject.short_name"
                            class="subj-toc-li__div subj-toc-li__div--bold subj-toc-li__abbr"
                        >
                            {{ subject.abbreviation || subject.short_name }}
                        </div>
                        <div
                            class="subj-toc-li__div subjects-toc-li__full-name"
                            :class="
                                !subject.abbreviation &&
                                !subject.short_name &&
                                'subj-toc-li__div--bold'
                            "
                        >
                            {{ subject.full_name }}
                        </div>
                    </router-link>
                    <div class="subj-toc-li__count" style="display: none">
                        <span class="subj-doc__count">0</span> formal and
                        <span class="subj-doc__count">0</span> informal
                        documents
                    </div>
                </li>
            </ul>
        </template>
    </div>
</template>

<style></style>
