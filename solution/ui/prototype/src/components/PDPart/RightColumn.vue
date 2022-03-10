<template>
    <div style="width: 100%; margin: 20px">
        <div>
            <h2 style="display: inline">Part {{ part }} resources</h2>
            <span style="float: right">
                <a>Filter and sort resources</a>
            </span>
        </div>
        <div>
            <v-text-field clearable outlined class="sidebar-search"> </v-text-field>
        </div>
        <TabFilters
            v-bind:title="title"
            v-bind:part="part"
            v-bind:subparts="subparts"
        />
    </div>
</template>

<script>
import TabFilters from "./TabFilters.vue";
export default {
    components: {
        TabFilters,
    },
    name: "RightColumn",
    props: {
        title: { type: Number },
        part: { type: Number },
        subparts: { type: Array, required: false },
    },
    data() {
        return {
            tabs: null,
            text: "djfdhkf",
        };
    },
};
</script>

<style>
.sidebar-search.v-text-field.v-text-field--enclosed {
    width: 95% !important;
}
.v-slide-group__content {
    border-bottom: 1px black solid;
}
</style>