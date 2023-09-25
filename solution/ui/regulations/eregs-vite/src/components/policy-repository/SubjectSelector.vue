<script setup>
import { inject } from "vue";

import { getSubjectName } from "utilities/filters";

const props = defineProps({
    policyDocSubjects: {
        type: Object,
        default: () => ({ results: [], loading: true }),
    },
});

const { updateSelectedParams } = inject("selectedParams");

const subjectClick = (event) => {
    updateSelectedParams({
        type: "subjects",
        action: "add",
        id: event.target.dataset.id,
        name: event.target.dataset.name,
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
                    :title="subject.full_name"
                    @click="subjectClick"
                >
                    {{ getSubjectName(subject) }}
                </button>
            </li>
        </ul>
    </div>
</template>
