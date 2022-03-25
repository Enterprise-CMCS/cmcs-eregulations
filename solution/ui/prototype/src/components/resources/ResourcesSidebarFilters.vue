<template>
    <div class="sidebar-filters-container">
        <div class="content">
            <div class="sidebar-header">Filter Resources</div>
            <template>
                <v-expansion-panels multiple>
                    <v-expansion-panel
                        class="panel-container"
                        v-for="(value, name) in filters"
                        :key="name"
                    >
                        <v-expansion-panel-header class="panel-header">
                            {{ value.label }}
                        </v-expansion-panel-header>
                        <v-expansion-panel-content class="panel-content">
                            {{ value.listItems }}
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
.sidebar-header {
    font-size: 15px;
    font-weight: bold;
    margin-bottom: 10px;
}

.sidebar-filters-container {
    overflow: auto;
    width: 100%;
    padding-bottom: 30px;
    margin: 40px 50px 0;
}

.panel-container {
    border-bottom: 1px solid #DDD;
}
.panel-header {
    font-size: 13px;
    font-weight: bold;
    color: black;
}

.v-expansion-panel-content .v-expansion-panel-content__wrap {
    max-height: 250px;
    overflow: scroll;
}
</style>
