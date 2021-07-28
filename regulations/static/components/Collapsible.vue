<template>
    <div
        ref="target"
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
            this.isVertical = this.direction === "vertical";
            this.setTabIndex(this.childtag, this.visible);
        });
        this.$root.$on("collapse-toggle", this.toggle);
    },

    mounted: function () {
        window.addEventListener("resize", this.resize);
    },

    destroyed: function () {
        window.removeEventListener("resize", this.resize);
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
            default: "1s",
        },
        direction: {
            //horizontal or vertical
            type: String,
            required: true,
        },
        childtag: {
            //html element to show/hide tabindex
            type: String,
            required: false,
        },
    },

    data: function () {
        return {
            size: "auto",
            visible: false,
            isVertical: true,
            styles: {
                overflow: "hidden",
                transition: this.transition,
            },
        };
    },

    computed: {
        sizeStyle: function () {
            return this.isVertical
                ? { height: this.size }
                : { width: this.size };
        },
    },

    methods: {
        setTabIndex: function (childtag, isVisible) {
            if (!childTag) return;

            // collapsed content should have tabIndex="-1" when collapsed
            // and tabIndex="0" when expanded.
            // Pass in tag name to toggle
            const children = Array.from(
                this.$el.getElementsByTagName(childtag)
            );
            children.map((child) => {
                const tabIndexVal = isVisible ? "0" : "-1";
                child.setAttribute("tabindex", tabIndexVal);
            });
        },
        resize: function (e) {
            this.computeSize();
        },
        toggle: function (target) {
            if (this.name === target) {
                requestAnimationFrame(() => {
                    this.computeSize();
                    requestAnimationFrame(() => {
                        this.visible = !this.visible;
                        this.setTabIndex(this.childtag, this.visible);
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
            if (this.isVertical) {
                this.$refs.target.style.height = size;
            } else {
                this.$refs.target.style.width = size;
            }
        },
        _computeSize: function () {
            if (this.getStyle().display === "none") {
                return "auto";
            }

            this.$refs.target.classList.remove("invisible");

            this.setProps("hidden", "block", "absolute", "auto");

            const size = this.isVertical
                ? this.getStyle().height
                : this.getStyle().width;

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
