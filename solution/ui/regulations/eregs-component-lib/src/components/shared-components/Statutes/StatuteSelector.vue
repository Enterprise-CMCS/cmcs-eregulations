<script setup>
import { computed, inject, onBeforeMount } from "vue";

const props = defineProps({
    selectedAct: {
        type: String,
        required: false,
        default: "ssa",
    },
    selectedTitle: {
        type: String,
        required: false,
        default: "19",
    },
    titles: {
        type: Object,
        required: false,
        default: () => {},
    },
});

const router = inject("router");

const tabRef = defineModel("tabModel", {
    type: Number,
    default: 0,
});

const selectedTitles = computed(() => {
    return props.titles[props.selectedAct]?.titles || [];
});

const getSelectedTitleIndex = () => {
    return selectedTitles.value.findIndex(
        (title) => title.title === props.selectedTitle
    );
};

onBeforeMount(() => {
    tabRef.value = getSelectedTitleIndex();
});

const updateRouterOnClick = (title) => {
    router.push({
        name: "statutes",
        query: {
            act: props.selectedAct,
            title: title.title,
        },
    });
};

</script>

<template>
    <v-tabs
        v-model="tabRef"
        class="acts__tabs"
        grow
    >
        <v-tab
            v-for="(title, i) in selectedTitles"
            :key="`${title.title}-${i}`"
            :data-testid="`${selectedAct}-${title.titleRoman}-${title.title}`"
            class="content-tabs"
            tabindex="0"
            @click="updateRouterOnClick(title)"
        >
            <span class="prefix__span">Title </span>{{ title.titleRoman }}
        </v-tab>
    </v-tabs>
</template>
