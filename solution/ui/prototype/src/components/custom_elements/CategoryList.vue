<template>
    <v-list dense>
        <v-list-item-group>
            <v-list-item @click="clickMethod" data-value="one">
                Category One
            </v-list-item>
            <v-list-item @click="clickMethod" data-value="two">
                Category Two
            </v-list-item>
        </v-list-item-group>
    </v-list>
</template>

<script>
export default {
    name: "DefaultName",

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

    data() {
        return {
            dataProp: "value",
        }
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        clickMethod(e) {
            this.filterEmitter(e.currentTarget.dataset.value)
        },
    },

}
</script>

<style>

</style>

