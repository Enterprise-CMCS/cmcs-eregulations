<template>
    <div>
        <h3>Part Summary</h3>
        <p>Summary of the part</p>
        <ExpansionMenu
            v-bind:header="'Featured Topics'"
            v-bind:subpiece="'Topic'"
            v-bind:content="'content'"
            v-bind="'true'"
        />

        <ExpansionMenu
            v-bind:header="'Part ' + part + ' Federal Register Documents'"
            v-bind:subpiece="'Document'"
            v-bind:content="'content'"
            v-bind="'true'"
        />
        <ExpansionMenu
            v-bind:header="'Miscellaneous Resources not Tied to a Regulation'"
            v-bind:subpiece="'Misc.'"
            v-bind:content="'content'"
            v-bind="'true'"
        />
        <br />
        <v-btn color="#046791" class="white--text">View All Resources</v-btn>
    </div>
</template>
<script>
import ExpansionMenu from "./ExpansionMenu.vue";
export default {
    name: "PartSummary",
    components: {
        ExpansionMenu,
    },
    data: () => ({
        show: false,
        documentHeader: 'Part {{ part }} Federal Register Documents'
    }),
    props: {
        title: { type: Number },
        part: { type: Number },
    },
};
</script>

<style>
.v-expansion-panel-header {
    color: #046791;
    padding: 0px 0px;
    box-shadow: none;
}
.v-expansion-panel::before {
    box-shadow: none;
}
.v-expansion-panel:not(:first-child)::after {
    border: none;
}
</style>