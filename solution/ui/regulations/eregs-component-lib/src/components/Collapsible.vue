<template>
    <div
        ref="target"
        :data-test="dataName"
        :class="{ invisible: !visible }"
        :style="[styles]"
    >
        <slot />
    </div>
</template>

<script>
import eventbus from "../eventbus";

export default {
    name: "Collapsible",

    created: function () {
        requestAnimationFrame(() => {
            this.visible = this.state === "expanded";
            if (!this.visible) {
                this.$refs.target?.classList?.add("display-none");
            }
        });
        eventbus.on("collapse-toggle", this.toggle);
    },

    mounted: function () {
        window.addEventListener("resize", this.resize);
        window.addEventListener("transitionend", this.toggleDisplay);
    },

    unmounted: function () {
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
        overflow: {
            type: Boolean,
            required: false,
            default: false,
        },
    },

    data: function () {
        return {
            dataName: this.name,
            height: "auto",
            visible: false,
            styles: {
                transition: this.transition,
                overflow: "hidden",
            },
        };
    },

    methods: {
        resize: function () {
            this.computeHeight();
        },
        toggleDisplay: function () {
            if (this.visible) {
                this.$refs.target.style.height = "auto";
                if (this.state === "collapsed" && this.overflow) {
                    this.$refs.target.style.overflow = "visible";
                }
            } else if (this.$refs.target) {
                this.$refs.target.classList.add("display-none");
                this.$refs.target.style.oveflow = "hidden";
            }
        },
        toggle: function (target) {
            if (this.dataName === target) {
                if (this.$refs.target) {
                    this.$refs.target.classList.remove("display-none");
                    this.$refs.target.style.overflow = "hidden";
                }
                requestAnimationFrame(() => {
                    this.computeHeight();
                    requestAnimationFrame(() => {
                        this.visible = !this.visible;
                    });
                });
            }
        },
        getStyle: function () {
            if (this.$refs.target) {
                return window.getComputedStyle(this.$refs.target);
            }
            return "auto";
        },
        setProps: function (visibility, display, position, height) {
            this.$refs.target.style.visibility = visibility;
            this.$refs.target.style.display = display;
            this.$refs.target.style.position = position;
            this.$refs.target.style.height = height;
        },
        computeHeightInternal: function () {
            if (this.getStyle().display === "none") {
                return "auto";
            }

            if (this.$refs.target) {
                this.$refs.target.classList.remove("invisible");
                this.setProps("hidden", "block", "absolute", "auto");
            }

            const height = this.getStyle().height;

            if (this.$refs.target) {
                this.setProps(null, null, null, height);
            }

            if (!this.visible && this.$refs.target) {
                this.$refs.target.classList.add("invisible");
            }
            return height;
        },
        computeHeight: function () {
            this.height = this.computeHeightInternal();
        },
    },
};
</script>
