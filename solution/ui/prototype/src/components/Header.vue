<template>
    <header id="header" :class="stickyClass">
        <!-- desktop -->
        <div class="flexbox header-large">
            <div class="title-container">
                <SiteTitle />
                <JumpTo />
            </div>
            <div class="links-container">
                <router-link :to="{ name: 'resources' }" class="header-link">
                    Resources
                </router-link>
                <router-link :to="{ name: 'about' }" class="header-link">
                    About
                </router-link>
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

    mounted() {
        window.addEventListener("scroll", this.onScroll);
    },

    beforeDestroy() {
        window.removeEventListener("scroll", this.onScroll);
    },

    props: {
        stickyMode: {
            validator: function (value) {
                return ["hideOnScrollDown", "normal", "disabled"].includes(
                    value
                );
            },
            default: "normal",
        },
    },

    data() {
        return {
            action: "open",
            state: "expanded",
            showNavbar: true,
            lastScrollPosition: 0,
        };
    },

    computed: {
        stickyClass() {
            return this.stickyMode === "hideOnScrollDown" || "normal"
                ? "sticky"
                : "";
        },
    },

    methods: {
        toggleState(payload) {
            this.action = payload.action;
            this.state = payload.state;
        },
        onScroll() {
            if (this.stickyMode === "hideOnScrollDown") {
                const scrollPosition = window.scrollY;
                const scrollDirection =
                    scrollPosition > this.lastScrollPosition ? "down" : "up";

                this.lastScrollPosition = scrollPosition;

                if (scrollDirection === "down") {
                    console.log("hide header!");
                    this.showNavbar = false;
                } else {
                    console.log("show header!");
                    this.showNavbar = true;
                }
            }
        },
    },
};
</script>

<style scoped>
header {
    box-sizing: border-box;
    border: 1px solid #d6d7d9;
}
.links-container {
    padding-right: 10px;
}

.header-search-container {
    border-left: 1px #d6d7d9 solid;
    padding: 10px 0 10px 18px;
}

.header-link {
    color: #212121;
    padding-right: 20px;
}
</style>
