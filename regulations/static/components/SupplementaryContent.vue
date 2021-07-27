<template>
  <div class="supplementary-content">
    <a class="supplementary-content-link external-link" :href="url" target="_blank" rel="noopener noreferrer">
      <span class="supplementary-content-date" v-if="date">{{ date|formatDate }}</span> <span class="supplementary-content-title">{{ title }}</span>
      <div class="supplementary-content-description">{{ description }}</div>
    </a>
  </div>
</template>

<script>

export default {
  name: 'supplementary-content',

  props: {
    title: {
      type: String,
      required: true,
    },
    description: {
        type: String,
        required: false,
    },
    date: {
        type: String,
        required: false,
    },
    url: {
      type: String,
      required: true,
    },
  },

  computed: {

  },

  methods: {},
  filters: {
    formatDate: function(value) {
      const date = new Date(value);
      const options = { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' };
      const format = new Intl.DateTimeFormat("en-US", options);
      return format.format(date);
    }
  }
};
</script>
