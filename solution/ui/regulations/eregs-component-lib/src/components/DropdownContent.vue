<template>
    <div v-if="active" class="dropdown-content">
        <ul class="dropdown-list">
            <slot />
        </ul>
    </div>
</template>

<script>
export default {
    name: 'DropdownContent',
    props: {
        active: {
            type: Boolean,
            default: false
        },
    },
}
</script>
