<script setup></script>

<template>
    <div class="result">
        <slot name="labels"></slot>
        <div class="result__context">
            <slot name="context"></slot>
        </div>
        <div class="result__link">
            <slot name="link"></slot>
        </div>
        <div class="result__snippet">
            <slot name="snippet"></slot>
        </div>
        <slot name="sections"></slot>
    </div>
</template>

<style></style>
