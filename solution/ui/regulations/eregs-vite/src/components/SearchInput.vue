<script setup>
import { ref, computed, watch, inject } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
    disabled: {
        type: Boolean,
        default: false,
    },
    formClass: {
        type: String,
        required: true,
    },
    label: {
        type: String,
        required: true,
    },
    searchQuery: {
        type: String,
        default: undefined,
    },
    synonyms: {
        type: Array,
        default: () => [],
    },
    showSuggestions: {
        type: Boolean,
        default: false,
    },
    redirectTo: {
        type: String,
        default: undefined,
    },
});

const emit = defineEmits(['execute-search', 'clear-form']);

const parent = inject('parent', 'search');
const router = useRouter();

const searchInputValue = ref(props.searchQuery);

const multiWordQuery = computed(() => {
    if (props.searchQuery === undefined) return false;
    return (
        props.searchQuery.split(' ').length > 1 &&
        props.searchQuery[0] !== '"' &&
        props.searchQuery[props.searchQuery.length - 1] !== '"'
    );
});

const submitForm = () => {
    emit('execute-search', { query: searchInputValue.value });
    searchInputValue.value = undefined;
};

const clearForm = () => {
    searchInputValue.value = undefined;
    emit('clear-form');
};

const updateSearchValue = (value) => {
    searchInputValue.value = value;
};

const synonymLink = (synonym) => {
    router.push({
        name: props.redirectTo || parent,
        query: {
            ...router.currentRoute.value.query,
            page: undefined,
            q: `"${synonym}"`,
        },
    });
};

const quotedLink = () => {
    router.push({
        name: props.redirectTo || parent,
        query: {
            ...router.currentRoute.value.query,
            page: undefined,
            q: `"${props.searchQuery}"`,
        },
    });
};

watch(
    () => props.searchQuery,
    (newQuery) => {
        searchInputValue.value = newQuery;
    }
);
</script>

<template>
    <form
        ref="formRef"
        :class="formClass"
        @submit.prevent="submitForm"
    >
        <v-text-field
            id="main-content"
            ref="searchInput"
            v-model="searchInputValue"
            :disabled="disabled"
            clearable
            variant="outlined"
            density="compact"
            :label="label"
            :aria-label="label"
            type="input"
            class="search-field"
            clear-icon="mdi-close"
            hide-details
            single-line
            @update:model-value="updateSearchValue"
        >
            <template #clear>
                <v-icon
                    title="Clear All"
                    aria-label="Clear search form"
                    icon="mdi-close"
                    data-testid="clear-search-form"
                    tabindex="-1"
                    @click="clearForm"
                />
            </template>
            <template #append-inner>
                <v-icon
                    icon="mdi-magnify"
                    :aria-label="`Search${searchInputValue ? ' for ' + searchInputValue : ''}`"
                    data-testid="search-form-submit"
                    @click="submitForm"
                    @keydown.enter.space.prevent="submitForm"
                />
            </template>
        </v-text-field>
        <div class="form-helper-text">
            <template v-if="showSuggestions && multiWordQuery">
                <div class="search-suggestion">
                    Didn't find what you were looking for? Try searching for
                    <a
                        tabindex="0"
                        @click="quotedLink"
                        @keydown.enter.space.prevent="quotedLink"
                    >"{{ searchQuery }}"</a>
                </div>
            </template>
            <template v-if="synonyms.length > 0">
                <div class="search-suggestion">
                    <span v-if="showSuggestions && multiWordQuery">
                        Or search
                    </span>
                    <span v-else> Search </span>
                    for similar terms:
                    <template v-for="(syn, i) in synonyms" :key="i">
                        <a
                            tabindex="0"
                            @click="synonymLink(syn)"
                            @keydown.enter.space.prevent="synonymLink(syn)"
                        >{{ syn }}</a><span
                            v-if="synonyms[synonyms.length - 1] != syn"
                        >,
                        </span>
                    </template>
                </div>
            </template>
        </div>
    </form>
</template>
