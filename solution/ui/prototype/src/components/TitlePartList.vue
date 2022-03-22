<template>
    <v-list dense>
        <v-list-item-group>
            <v-list-item @click="clickMethod" data-value="one">
                Do I need anything else?
            </v-list-item>
            <v-list-item @click="clickMethod" data-value="two">
                how about now
            </v-list-item>
        </v-list-item-group>
    </v-list>
</template>

<script>
export default {
    name: "TitlePartList",

    components: {},

    props: {
        filterEmitter: {
            type: Function,
            required: true,
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    /*data() {
        return {
            dataProp: "value",
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },*/

    methods: {
        clickMethod(e) {
            this.filterEmitter(e.currentTarget.dataset.value)
        },
    },
};
</script>

<style></style>
