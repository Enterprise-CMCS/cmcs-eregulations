<template>
    <span v-if="item.reserved" class="reserved toc-link">{{item.label}}</span>
    <a v-else @click="doNavigation(item)" class="toc-link">
        <span style="font-weight:700">{{item.label_level}}</span>
        {{item.label_description}}
    </a>
</template>

<script>

export default {
    name: "TOCSection",

    components: {

    },

    props: {
      doNavigation: {
          type: Function,
          required: true,
      },
      item: {type: Object}
    },

    computed: {

    },

    methods: {
    },
};
</script>


