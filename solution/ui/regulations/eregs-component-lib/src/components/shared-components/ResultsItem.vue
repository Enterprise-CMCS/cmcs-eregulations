<script setup></script>

<template>
    <div class="result">
        <div class="category-labels">
            <slot name="labels"></slot>
        </div>
        <div class="result__context">
            <slot name="context">
                <div style="margin-bottom: -8px"></div>
            </slot>
        </div>
        <div class="result__link">
            <slot name="link">
                <div style="margin-bottom: -8px"></div>
            </slot>
        </div>
        <div class="result__snippet">
            <slot name="snippet"></slot>
        </div>
        <slot name="resources-content"></slot>
        <slot name="chips"></slot>
        <slot name="sections"></slot>
    </div>
</template>
