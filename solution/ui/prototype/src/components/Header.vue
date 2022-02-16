<template>
    <header id="header" class="sticky">
        <!-- desktop -->
        <div class="flexbox header-large">
            <div class="title-container">
                <SiteTitle />
                <JumpTo />
            </div>
            <div class="links-container">
                <a class="header-links-container" href="">Resources</a>
                <a class="header-links-container" href="">About</a>
            </div>
            <div class="header-search-container">
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
import JumpTo from "./JumpTo.vue";

export default {
    name: "Header",

    components: {
        RegTitle,
        SearchInput,
        SiteTitle,
        ToggleButton,
        JumpTo,
    },

    data() {
        return {
            action: "open",
            state: "expanded",
        };
    },

    methods: {
        toggleState(payload) {
            this.action = payload.action;
            this.state = payload.state;
        },
    },
};
</script>

<style>
header {
    box-sizing: border-box;
    border: 1px solid #d6d7d9;
}
.links-container {
    padding-right: 10px;
}

.header-links-container {
    padding-right: 20px;
    color: #212121;
}
.site-title {
    padding: 10px;
}
.header-search-container {
    border-left: 1px #ddf5fd;
}
</style>
