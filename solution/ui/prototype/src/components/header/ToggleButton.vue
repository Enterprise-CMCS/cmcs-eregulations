<template>
    <button
        :id="buttonId"
        :data-set-state="setState"
        :data-state="setState"
        :aria-label="buttonAriaLabel"
        @click="handleClick"
    >
        <svg
            :width="iconWidth"
            height="20"
            :viewBox="iconViewBox"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            aria-labelledby="title"
        >
            <path
                v-if="action == 'open'"
                d="M14.9012 8.09846C14.9012 4.59913 11.9002 1.79966 8.3819 1.79966C4.76009 1.79966 1.86265 4.59913 1.86265 8.09846C1.86265 11.4978 4.76009 14.3973 8.3819 14.3973C11.9002 14.3973 14.9012 11.4978 14.9012 8.09846ZM15.2116 12.6976L21.2135 18.3965C22.0413 19.2963 20.7995 20.5961 19.8682 19.6963L13.9698 13.9973C12.5211 15.3971 10.555 16.1969 8.3819 16.1969C3.72529 16.1969 0 12.4976 0 8.09846C0 3.59932 3.72529 0 8.3819 0C12.935 0 16.7638 3.59932 16.7638 8.09846C16.7638 9.79814 16.1429 11.3978 15.2116 12.6976Z"
                fill="#046791"
            />
            <path
                v-else
                fill-rule="evenodd"
                clip-rule="evenodd"
                d="M1.99781 15L15.5794 1.41934C16.3551 0.643626 15.1915 -0.519885 14.4157 0.255821L0.252353 14.4182C0.0435553 14.627 -0.0247707 14.8639 0.00755119 15.1343C0.0343742 15.287 0.111331 15.4407 0.252353 15.5818L14.4157 29.7442C15.1915 30.5199 16.3551 29.3564 15.5794 28.5807L1.99781 15Z"
                fill="#046791"
            />
            <title
                :id="iconTitleId"
                lang="en"
            >
                {{ iconTitle }}
            </title>
        </svg>
    </button>
</template>

<script>
export default {
    name: "ToggleButton",

    props: {
        action: {
            type: String,
            required: true,
        },
        setState: {
            type: String,
            required: true,
        },
        title: {
            type: String,
            required: true,
        },
    },

    computed: {
        buttonAriaLabel() {
            return `${this.action} search bar`;
        },
        buttonId() {
            return `mobile-search-${this.action}`;
        },
        iconTitle() {
            return `${this.action === "open" ? "Open" : "Leave"} Search`;
        },
        iconTitleId() {
            return `search-header-${this.action}-icon`;
        },
        iconViewBox() {
            return `0 0 ${this.action === "open" ? "22 20" : "16 30"}`;
        },
        iconWidth() {
            return this.action === "open" ? "22" : "16";
        },
    },

    methods: {
        handleClick() {
            this.$emit("handle-click", {
                action: this.action === "open" ? "close" : "open",
                state: this.action === "open" ? "collapsed" : "expanded",
            });
        },
    },
};
</script>

<style></style>
