<template>
    <div class="sidebar-filters-container">
        <div class="content" :class="resourcesClass">
            FILTER SIDEBAR HERE
            <template>
                <v-expansion-panels multiple>
                    <v-expansion-panel
                        v-for="(value, name) in filters"
                        :key="name"
                    >
                        <v-expansion-panel-header>
                            {{ name }}
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                            {{ value }}
                        </v-expansion-panel-content>
                    </v-expansion-panel>
                </v-expansion-panels>
            </template>
        </div>
    </div>
</template>

<script>
export default {
    name: "ResourcesSidebarFilters",

    components: {},

    props: {
        resourcesDisplay: {
            type: String,
            required: false,
        },
        filters: {
            type: Object,
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
        };
    },

    computed: {
        computedProp() {
            return this.dataProp.toUpperCase();
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },
};
</script>

<style>
.sidebar-filters-container {
    overflow: auto;
    width: 100%;
    padding-bottom: 30px;
    margin: 40px 50px 0;
}
</style>
