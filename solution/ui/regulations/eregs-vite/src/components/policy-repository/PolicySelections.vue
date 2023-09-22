<script setup>
import { inject, ref, watch } from "vue";

const SubjectsEnum = {
    subjects: "Subject",
};

const { selectedParamsObj, updateSelectedParams } = inject("selectedParams");

const subjectClick = (event) => {
    updateSelectedParams({
        type: "subjects",
        action: "remove",
        id: event.target.dataset.id,
    });
};

const selections = ref({});

watch(
    () => selectedParamsObj.paramString,
    async (newParamsObj) => {
        // map over selectedParamsObj.params and reduce to an array of objects with key = type and value = id
        selections.value = Object.entries(
            selectedParamsObj.params
        ).reduce((acc, [key, value]) => {
            const ids = value.split(",");
            ids.forEach((id) => {
                acc.push({ label: SubjectsEnum[key], type: key, id });
            });
            return acc;
        }, [])
        .sort((a, b) => { // sort by label and then by id
            if (a.label < b.label) return -1;
            if (a.label > b.label) return 1;
            if (a.id < b.id) return -1;
            if (a.id > b.id) return 1;
            return 0;
        });

    }
);
</script>

<template>
    <div class="selections__container">
        <ul>
            <li v-for="selection in selections" :key="selection.id">
                {{ selection.label }}: {{ selection.id }}
                <button
                    :data-id="selection.id"
                    @click="subjectClick"
                >
                x
                </button>
            </li>
        </ul>
    </div>
</template>
