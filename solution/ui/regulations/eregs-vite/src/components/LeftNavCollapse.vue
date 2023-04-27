<script setup>
import { ref } from "vue";

// open or closed
const drawerOpen = ref(true);

// Russian doll, slots all the way down
// This component is specifically for left nav with open/close abilities
// Column that collapses/expands horizontally for wide widths. Will have a max width
// Column that collapses/expands vertically from top for narrow widths.  Will be full width
// this component will:
// 1. open and close
// 2. have a max width (prop?)
</script>

<template>
    <nav id="leftNav">
        <button class="nav-toggle__button">X</button>
        <v-btn outlined color="indigo">
            <v-icon>mdi-close</v-icon>
        </v-btn>
        <slot></slot>
    </nav>
</template>

<style>
#leftNav {
    background-color: #f5f5f5;
    border-right: 1px solid #e0e0e0;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    height: 100%;
    width: 400px;
}
</style>
