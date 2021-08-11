<template>
    <div
        ref="target"
        v-bind:data-test="name"
        v-bind:class="{ invisible: !visible }"
        v-bind:style="[styles, sizeStyle]"
    >
        <slot></slot>
    </div>
</template>

<script>
export default {
    name: "collapsible",

    created: function () {
        requestAnimationFrame(() => {
            this.visible = this.state === "expanded";
            if (!this.visible) {
                this.$refs.target.classList.add("display-none");
            }
        });
        this.$root.$on("collapse-toggle", this.toggle);
    },

    mounted: function () {
        window.addEventListener("resize", this.resize);
        window.addEventListener("transitionend", this.toggleDisplay);
    },

    destroyed: function () {
        window.removeEventListener("resize", this.resize);
        window.removeEventListener("transitionend", this.toggleDisplay);
    },

    props: {
        name: {
            type: String,
            required: true,
        },
        state: {
            //expanded or collapsed
            type: String,
            required: true,
        },
        transition: {
            type: String,
            required: false,
            default: "0.5s",
        },
    },

    data: function () {
        return {
            name: this.name,
            size: "auto",
            visible: false,
            styles: {
                overflow: "hidden",
                transition: this.transition,
            },
        };
    },

    computed: {
        sizeStyle: function () {
            return { height: this.size }
        },
    },

    methods: {
        resize: function (e) {
            this.computeSize();
        },
        toggleDisplay: function (e) {
            if (this.visible) {
                this.$refs.target.style.height = "auto";
            }
            else {
                this.$refs.target.classList.add("display-none");
            }
        },
        toggle: function (target) {
            if (this.name === target) {
                this.$refs.target.classList.remove("display-none");
                requestAnimationFrame(() => {
                    this.computeSize();
                    requestAnimationFrame(() => {
                        this.visible = !this.visible;
                    });
                });
            }
        },
        getStyle: function () {
            return window.getComputedStyle(this.$refs.target);
        },
        setProps: function (visibility, display, position, size) {
            this.$refs.target.style.visibility = visibility;
            this.$refs.target.style.display = display;
            this.$refs.target.style.position = position;
            this.$refs.target.style.height = size;
        },
        _computeSize: function () {
            if (this.getStyle().display === "none") {
                return "auto";
            }

            this.$refs.target.classList.remove("invisible");

            this.setProps("hidden", "block", "absolute", "auto");

            const size = this.getStyle().height;

            this.setProps(null, null, null, size);
            if (!this.visible) {
                this.$refs.target.classList.add("invisible");
            }
            return size;
        },
        computeSize: function () {
            this.size = this._computeSize();
        },
    },
};
</script>
