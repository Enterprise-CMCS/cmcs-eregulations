<template>
  <div @click="toggleButton()" class="show-more-button">
    <b>{{ buttonText }}</b> ({{count}})
  </div>
</template>

<script>
export default {
  name: 'show-more-button',
  props: {
    count: {
      type: Number,
      default: 1
    },
  },
  data() {
    return {
      toggle: false,
    }
  },
  computed: {
    buttonText(){
      return this.toggle ? '- Show Less' : '+ Show More';
    }
  },
  methods: {
    toggleButton() {
      this.toggle = !this.toggle
    }
  }
};
</script>
