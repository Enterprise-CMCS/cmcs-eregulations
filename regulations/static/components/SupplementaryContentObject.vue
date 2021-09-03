<template>
  <div class="supplementary-content">
    <a class="supplementary-content-link" :href="url" target="_blank" rel="noopener noreferrer">
      <span class="supplementary-content-date" v-bind:class="{ 'supplementary-content-mid-bar': !isBlank(title) }" v-if="date">{{ date|formatDate }}</span>
      <span class="supplementary-content-title" v-bind:class="{ 'supplementary-content-external-link': isBlank(description) }" v-if="!isBlank(title)">{{ title }}</span>
      <div v-if="!isBlank(description)" class="supplementary-content-description supplementary-content-external-link">{{ description }}</div>
    </a>
  </div>
</template>

<script>

export default {
  name: 'supplementary-content-object',

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
  
  filters: {
    formatDate: function(value) {
      const date = new Date(value);
      let options = { year: 'numeric', timeZone: 'UTC' };
      const raw_date = value.split('-');
      if(raw_date.length > 1) {
        options.month = 'long';
      }
      if(raw_date.length > 2) {
        options.day = 'numeric';
      }
      const format = new Intl.DateTimeFormat("en-US", options);
      return format.format(date);
    }
  },

  methods: {
    isBlank: function(str) {
      return (!str || /^\s*$/.test(str));
    },
  },
};
</script>
