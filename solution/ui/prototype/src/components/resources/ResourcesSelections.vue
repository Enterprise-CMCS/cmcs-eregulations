<template>
    <div class="selections-container">
        <template v-for="(value, name, idx) in filterParams">
            <v-chip
                v-if="value && name !== 'title'"
                :key="value + name + idx"
                close
                @click:close="handleClose(value, name)"
            >
                {{ value }} {{ name }}
            </v-chip>
        </template>
    </div>
</template>

<script>
export default {
    name: "ResourcesSelections",

    components: {},

    props: {
        filterParams: {
            type: Object,
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
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        handleClose(value, name) {
            this.$emit("chip-filter", {
                scope: name,
                selectedIdentifier: value,
            });
        },
    },
};
</script>

<style></style>
