<template>
  <div class="supplemental-content">
    <a class="supplemental-content-link" :href="url" target="_blank" rel="noopener noreferrer">
      <span class="supplemental-content-date" v-bind:class="{ 'supplemental-content-mid-bar': !isBlank(name) }" v-if="date">{{ date|formatDate }}</span>
      <span class="supplemental-content-title" v-bind:class="{ 'supplemental-content-external-link': isBlank(description) }" v-if="!isBlank(name)">{{ name }}</span>
      <div
          v-if="!isBlank(description)"
          class="supplemental-content-description supplemental-content-external-link"
        >
          <span v-html="description"/>
        </div>
    </a>
  </div>
</template>

<script>

export default {
  name: 'supplemental-content-object',

  props: {
    name: {
      type: String,
      required: false,
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

<style>
.search-highlight{
    font-weight: bold;
}
</style>
