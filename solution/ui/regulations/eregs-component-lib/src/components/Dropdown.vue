<template>
    <div>
        <slot name="toggler" :toggle="toggle">
            <button
                v-clickaway="away"
                class="dropdown-button ds-c-field"
                @click="toggle"
            >
                {{ selection }}
            </button>
        </slot>
        <slot :active="active" />
    </div>
</template>

<script>
export default {
    name: 'Dropdown',
    props: {
        initialActive: {
            type: Boolean,
            required: true,
            default: false
        },
        selection: {
            type: String,
            required: true,
            default: "Select Date"
        }
    },
    data() {
        return {
            active: this.initialActive
        }
    },
    methods: {
        toggle() {
            this.active = !this.active
        },
        away() {
            this.active = false
        }
    }
}
</script>
