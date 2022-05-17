<template>
    <div style="padding-left: 5px; font-size: 12px; margin-top: -10px;">
      <a v-on:click="clickHandler">View {{this.section}} resources ({{this.count}})</a>
    </div>
</template>

<script>
import {EventCodes} from "../../utils";

export default {
    name: "ViewResourcesLink",

    props: {
        section: {
            type: Array,
            required: true,
        },
        count: {
            type: Number,
            required: true,
        },
    },
    methods: {
      clickHandler(){
        this.$root.$emit(EventCodes.SetSection, {section: this.section, count: this.count})
      }
    },
};
</script>

//YOLO!!