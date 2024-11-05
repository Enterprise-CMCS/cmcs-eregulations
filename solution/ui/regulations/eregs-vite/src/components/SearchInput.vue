<template>
    <form ref="formRef" :class="formClass" @submit.prevent="submitForm">
        <v-text-field
            id="main-content"
            ref="searchInput"
            v-model="searchInputValue"
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
                    :aria-label="`Search for ${searchInputValue}`"
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
                        :key="i"
                        tabindex="0"
                        @click="quotedLink"
                        @keydown.enter.space.prevent="quotedLink"
                        >"{{ searchQuery }}"</a
                    >
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
                            >{{ syn }}</a
                        ><span
                            v-if="synonyms[synonyms.length - 1] != syn"
                            :key="i"
                            >,
                        </span>
                    </template>
                </div>
            </template>
        </div>
    </form>
</template>

<script>
export default {
    name: "DefaultName",

    components: {},

    props: {
        formClass: {
            type: String,
            required: true,
        },
        label: {
            type: String,
            required: true,
        },
        parent: {
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
    },

    created() {
        if (this.parent !== "subjects") {
            this.searchInputValue = this.searchQuery;
        }
    },
    data() {
        return {
            searchInputValue: undefined,
        };
    },

    computed: {
        multiWordQuery() {
            if (this.searchQuery === undefined) return false;

            return (
                this.searchQuery.split(" ").length > 1 &&
                this.searchQuery[0] !== '"' &&
                this.searchQuery[this.searchQuery.length - 1] !== '"'
            );
        },
    },

    methods: {
        submitForm() {
            this.$emit("execute-search", { query: this.searchInputValue });

            // clear search input so input is clear if user clicks back button
            // to return to this page
            this.$refs.searchInput.reset();
        },
        clearForm() {
            this.searchInputValue = undefined;
            this.$emit("clear-form");
        },
        updateSearchValue(value) {
            this.searchInputValue = value;
        },
        synonymLink(synonym) {
            this.$router.push({
                name: this.redirectTo || this.parent,
                query: {
                    ...this.queryParams,
                    page: undefined,
                    q: `"${synonym}"`,
                },
            });
        },
        quotedLink() {
            this.$router.push({
                name: this.redirectTo || this.parent,
                query: {
                    ...this.queryParams,
                    page: undefined,
                    q: `"${this.searchQuery}"`,
                },
            });
        },
    },

    watch: {
        searchQuery: {
            async handler(newQuery) {
                this.searchInputValue = newQuery;
            },
        },
    },
};
</script>
