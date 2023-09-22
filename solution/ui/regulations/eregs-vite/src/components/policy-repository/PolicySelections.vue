<script setup>
import { inject, ref, watch } from "vue";

const SubjectsEnum = {
    subjects: "Subject",
};

const { selectedParams, updateSelectedParams } = inject("selectedParams");

const subjectClick = (event) => {
    updateSelectedParams({
        type: "subjects",
        action: "remove",
        id: event.target.dataset.id,
    });
};

const selections = ref({});

watch(
    () => selectedParams.paramString,
    async () => {
        selections.value = selectedParams.paramsArray.map((param) => {
            return { label: SubjectsEnum[param.type], id: param.id, name: param.name };
        })
        .sort((a, b) => { // sort by label and then by id
            if (a.label < b.label) return -1;
            if (a.label > b.label) return 1;
            if (a.name < b.name) return -1;
            if (a.name > b.name) return 1;
            return 0;
        });
    }
);
</script>

<template>
    <div class="selections__container">
        <ul>
            <li v-for="selection in selections" :key="selection.id">
                {{ selection.label }}: {{ selection.name }} {{ selection.id }}
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
