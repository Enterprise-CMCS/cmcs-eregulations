<script setup>
import { computed, onBeforeMount } from "vue";

const props = defineProps({
    loading: {
        type: Boolean,
        required: false,
        default: false,
    },
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

</script>

<template>
    <v-tabs
        v-model="tabRef"
        grow
    >
        <v-tab
            v-for="(title, i) in selectedTitles"
            :key="`${title.title}-${i}`"
            class="content-tabs"
            tabindex="0"
            @click="() => { console.log('Tab clicked:', title.titleRoman); }"
        >
            Title {{ title.titleRoman }}
        </v-tab>
    </v-tabs>
    <!-- ul class="acts__list">
        <li
            v-for="(value, key, i) in titles"
            :key="`${key}-${i}`"
            class="acts-list__item"
        >
            <h4
                class="acts-item__heading"
                :class="{
                    'acts-item__heading--active': isActActive({ act: key }),
                }"
            >
            </h4>
            <ul class="titles__list">
                <li
                    v-for="(title, j) in value.titles"
                    :key="`${title.title}-${j}`"
                    class="titles-list__item"
                >
                    <h4>
                        <RouterLink
                            class="titles-list__link"
                            :data-testid="`${key}-${title.titleRoman}-${title.title}`"
                            :class="{
                                'titles-list__link--active': isTitleActive({
                                    act: key,
                                    title: title.title,
                                }),
                                'titles-list__link--loading': loading,
                            }"
                            :to="{
                                name: 'statutes',
                                query: {
                                    act: key,
                                    title: title.title,
                                },
                            }"
                        >
                            Title {{ title.titleRoman }}
                        </RouterLink>
                    </h4>
                </li>
            </ul>
        </li>
    </ul -->
</template>
