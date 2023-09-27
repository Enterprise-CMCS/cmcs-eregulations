<script setup>
import { useRouter, useRoute } from "vue-router/composables";

import { getSubjectName } from "utilities/filters";

const props = defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
});

const $router = useRouter();
const $route = useRoute();

const subjectClick = (event) => {
    const subjects = $route.query.subjects
        ? $route.query.subjects.split(",")
        : [];

    if (subjects.includes(event.target.dataset.id)) return;

    subjects.push(event.target.dataset.id);

    $router.push({
        name: "policy-repository",
        query: {
            subjects: subjects.join(","),
        },
    });
};
</script>

<template>
    <div class="subjects__select-container">
        <h3>By Subject</h3>
        <ul tabindex="-1" class="subjects__list">
            <li
                v-for="subject in policyDocSubjects.results"
                :key="subject.id"
                class="subjects__li sidebar__li"
            >
                <button
                    :data-name="getSubjectName(subject)"
                    :data-id="subject.id"
                    :data-testid="`add-subject-${subject.id}`"
                    :title="subject.full_name"
                    @click="subjectClick"
                >
                    {{ getSubjectName(subject) }}
                </button>
            </li>
        </ul>
    </div>
</template>
