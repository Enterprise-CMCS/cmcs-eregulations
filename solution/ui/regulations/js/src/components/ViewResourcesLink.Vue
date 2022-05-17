<template>
    <div v-if="isLink" style="padding-left: 5px; font-size: 12px; margin-top: -10px;">
      <a v-if="this.count !== '0'" v-on:click="clickHandler">View {{this.section}} resources ({{ this.count }})</a>
      <a v-else>No resources for {{this.section}}</a>
    </div>
    <div v-else style="padding-left: 5px; font-size: 14px;">
      <button class="btn" v-if="this.count !== '0'" v-on:click="clickHandler">View {{this.section}} resources ({{ this.count }})</button>
      <button class="btn" v-else>No resources for {{this.section}}</button>
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
        type: {
          type: String,
          required: false,
          default: 'link'
        }
    },
    methods: {
      clickHandler(){
        this.$root.$emit(EventCodes.SetSection, {section: this.section, count: this.count})
      },
      isLink(){
        return this.type === 'link'
      }
    },
};
</script>

<style>
  .btn{
    background-color: #046791;
    color: #fff;
    border-radius: 3px;
    padding: 9px 10px 10px;
    border: none;
  }

</style>