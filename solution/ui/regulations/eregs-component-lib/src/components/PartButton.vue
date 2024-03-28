<template>
  <button
    class="dropdown-part-button"
    @click="toggle"
  >
    Part <i class="fas fa-chevron-down" />
  </button>
</template>

<script>

export default {
  name: 'part-button',
  props: {
    toggle: {type: Function},
    away: {type: Function}
  }
}
</script>
