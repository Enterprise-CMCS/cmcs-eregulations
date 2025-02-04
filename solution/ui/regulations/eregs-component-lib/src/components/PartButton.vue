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
    name: 'PartButton',
    props: {
        toggle: {type: Function, default: () => {}},
        away: {type: Function, default: () => {}}
    }
}
</script>
