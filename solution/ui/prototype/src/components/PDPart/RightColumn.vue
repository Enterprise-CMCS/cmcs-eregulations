<template>
    <div style="width: 100%; margin: 20px">
        <div>
            <h2 style="display: inline">Part {{ part }} resources</h2>
            <span style="float: right">
                <a>Filter and sort resources</a>
            </span>
        </div>
        <div>
            <v-text-field clearable outlined class="example"> </v-text-field>
        </div>
<TabFilters v-bind:title="title" v-bind:part="part"/>
    </div>
</template>

<script>
import TabFilters from "./TabFilters.vue"
export default {
    components: {
        TabFilters
    },
    name: "RightColumn",
    props: {
        title: { type: String },
        part: { type: String },
    },
    data(){
        return{
            tabs: null,
            text: 'djfdhkf'
        }
    }
};
</script>

<style>
.v-text-field.v-text-field--enclosed .v-input__slot {
    width: 90% !important;
    max-width: 90% !important;
}

</style>