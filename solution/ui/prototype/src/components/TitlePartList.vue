<template>
    <v-list dense>
        <v-list-item-group>
            <v-list-item @click="clickMethod">
                Do I need anything else?
            </v-list-item>
        </v-list-item-group>
    </v-list>
</template>

<script>
export default {
    name: "TitlePartList",

    components: {},

    props: {
        clickMethod: {
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
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style></style>
