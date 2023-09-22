<script setup>
import { inject } from "vue";

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
                    :data-name="
                        subject.short_name ||
                        subject.abbreviation ||
                        subject.full_name
                    "
                    :data-id="subject.id"
                    :title="subject.full_name"
                    @click="subjectClick"
                >
                    {{
                        subject.short_name ||
                        subject.abbreviation ||
                        subject.full_name
                    }}
                </button>
            </li>
        </ul>
    </div>
</template>
