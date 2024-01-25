<template>
    <form :class="formClass" @submit.prevent="submitForm">
        <v-text-field
            id="main-content"
            v-model="searchInputValue"
            outlined
            flat
            solo
            clearable
            :label="label"
            :aria-label="label"
            type="text"
            class="search-field"
            append-icon="mdi-magnify"
            hide-details
            dense
            @input="updateSearchValue"
            @click:append="submitForm"
            @click:clear="clearForm"
        />
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
                    <span v-if="showSuggestions && multiWordQuery"> Or search </span>
                    <span v-else> Search </span>
                    for similar terms:
                    <template v-for="(syn, i) in synonyms">
                        <a
                            :key="i"
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
        page: {
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
    },

    created() {
        this.searchInputValue = this.searchQuery;
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
        },
        clearForm() {
            this.$emit("clear-form");
        },
        updateSearchValue(value) {
            this.searchInputValue = value;
        },
        synonymLink(synonym) {
            this.$router.push({
                name: this.page,
                query: {
                    ...this.queryParams,
                    page: undefined,
                    q: `"${synonym}"`,
                },
            });
        },
        quotedLink() {
            this.$router.push({
                name: this.page,
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

<style lang="scss">
.search-field {
    height: 40px;
    border-radius: 3px;

    .v-input__icon.v-input__icon--append button,
    .v-input__icon.v-input__icon--clear button {
        color: $mid_blue;
    }

    .v-input__icon.v-input__icon--clear button {
        padding-right: 2px;
        border-right: 1px solid $light_gray;
    }

    fieldset {
        border-radius: 3px;
        border: 1px solid $light_gray;
    }

    .v-input__control .v-input__slot {
        max-width: calc(100% - 24px);
    }
}

.form-helper-text {
    margin-top: 10px;
}
</style>
