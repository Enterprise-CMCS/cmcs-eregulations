<template>
    <header
        id="header"
        class="sticky"
    >
        <!-- desktop -->
        <div class="flexbox header-large">
            <div class="title-container">
                <SiteTitle />
                <RegTitle />
            </div>

            <div class="search-header">
                <SearchInput type="search-box" />
            </div>
        </div>

        <!-- mobile -->
        <div class="flexbox header-mobile">
            <!-- titles -->
            <div
                class="mobile-titles"
                data-state-name="header-mobile-titles"
                :data-state="state"
            >
                <div class="title-container">
                    <SiteTitle />
                    <RegTitle />
                </div>
            </div>

            <!-- open search button -->
            <ToggleButton
                :action="action"
                :set-state="state"
                title="Search"
                @handle-click="toggleState"
            />

            <SearchInput type="search-borderless" />
        </div>
    </header>
</template>

<script>
import RegTitle from "@/components/header/RegTitle.vue";
import SearchInput from "@/components/header/SearchInput.vue";
import SiteTitle from "@/components/header/SiteTitle.vue";
import ToggleButton from "@/components/header/ToggleButton.vue";

export default {
    name: "Header",

    components: {
        RegTitle,
        SearchInput,
        SiteTitle,
        ToggleButton,
    },

    data() {
        return {
            action: "open",
            state: "expanded",
        };
    },

    methods: {
        toggleState(payload) {
            console.log("from the child:", payload);
            this.action = payload.action;
            this.state = payload.state;
        },
    },
};
</script>

<style></style>
