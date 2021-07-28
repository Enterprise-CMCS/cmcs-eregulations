<template>
  <button @click="showMore" class="show-more-button">
    <b>+ Show More</b> ({{count}})
  </button>
</template>

<script>
export default {
  name: 'show-more-button',
  props: {
    count: {
      type: Number,
      default: 1
    },
    showMore: { type: Function },
  }
};
</script>
