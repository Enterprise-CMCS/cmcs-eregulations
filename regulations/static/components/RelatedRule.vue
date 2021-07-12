<template>
  <div class="related-rule recent-change">
    <a class="related-rule-title" :href="html_url">
      <span class="recent-flag indicator">{{ expandedType }}</span>
      <span class="recent-date" v-if="publication_date">{{ publication_date|formatDate }}</span> | <span class="recent-fr">{{ citation }}</span>
      <div class="recent-title">{{ title }}</div>
    </a>
  </div>
</template>

<script>

export default {
  name: 'related-rule',

  props: {
    title: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      required: true,
    },
    citation: {
      type: String,
      required: true,
    },
    publication_date: String,
    document_number: {
      type: String,
      required: true,
    },
    html_url: {
      type: String,
      required: true,
    },
  },

  computed: {
    expandedType: function() {
      if(this.type === "Rule") {
        return "Final";
      }
      return "Unknown";
    },
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
