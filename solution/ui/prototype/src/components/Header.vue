<template>
    <header id="header" :class="headerClasses">
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

    props: {
        stickyMode: {
            validator: function (value) {
                return ["hideOnScrollDown", "normal", "disabled"].includes(
                    value
                );
            },
            default: "normal",
        },
        showHeader: {
            type: Boolean,
            default: true,
        }
    },

    data() {
        return {
            action: "open",
            state: "expanded",
        };
    },

    computed: {
        headerClasses() {
            return {
                sticky: this.stickyMode === "hideOnScrollDown" || "normal",
                "sticky-hide": !this.showHeader,
            };
        },
    },

    methods: {
        toggleState(payload) {
            this.action = payload.action;
            this.state = payload.state;
        },
    },
};
</script>

<style scoped>
header {
    box-sizing: border-box;
    border: 1px solid #d6d7d9;
    transition: transform 0.3s ease-in-out;
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

.sticky-hide {
    box-shadow: none;
    transform: translate3d(0, -100%, 0);
}
</style>
