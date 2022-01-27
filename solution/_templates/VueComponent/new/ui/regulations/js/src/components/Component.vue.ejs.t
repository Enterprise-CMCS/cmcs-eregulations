---
to: ui/regulations/js/src/components/<%= name %>Component.vue
---
<template>
    <div>
      NEW COMPONENT
    </div>
</template>

<script>
export default {
    name: "<%= h.changeCase.lower(name) %>-component",

    props: {},

    methods: {},

    created: function () {},

    mounted: function () {},

    destroyed: function () {},

    data: function () {
        return {}
    }
};
</script>

