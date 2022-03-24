<template>
    <div class="selections-container">
        <template v-for="(array, name, idx) in splitParams">
            <div v-if="array && name !== 'title'" :key="array[0] + name + idx" class="chip-group">
                <v-chip
                    v-for="value in array"
                    :key="value + name + idx"
                    close
                    @click:close="handleClose(value, name)"
                >
                    {{ value }} {{ name }}
                </v-chip>
            </div>
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
        splitParams() {
            const splitParams = { ...this.filterParams };

            for (const key in splitParams) {
                if (splitParams[key]) {
                    splitParams[key] = splitParams[key].split(",");
                }
            }
            return splitParams;
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

<style>
.chip-group {
    display: inline;
}
</style>
