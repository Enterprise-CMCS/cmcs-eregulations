<script setup>
import { ref } from "vue";
import { getPolicyDocSubjects } from "utilities/api";

const props = defineProps({
    prop1: {
        type: String,
        required: true,
    },
    prop2: {
        type: Object,
        required: true,
    },
});

const policyDocSubjects = ref({
    results: [],
    loading: true,
});

const getDocSubjects = async () => {
    try {
        policyDocSubjects.value.results = await getPolicyDocSubjects({
            apiUrl: props.apiUrl,
        });
    } catch (error) {
        console.error(error);
    } finally {
        policyDocSubjects.value.loading = false;
    }
};

getDocSubjects();
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
                <RouterLink
                    class="subjects-li__link"
                    :data-testid="test"
                    :to="{
                        name: 'policy-repository',
                        query: {
                            subject: subject.id,
                        },
                    }"
                >
                    {{
                        subject.short_name ||
                        subject.abbreviation ||
                        subject.full_name
                    }}
                </RouterLink>
            </li>
        </ul>
    </div>
</template>

<style></style>
