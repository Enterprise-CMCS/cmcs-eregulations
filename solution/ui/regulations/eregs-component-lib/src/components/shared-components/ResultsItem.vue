<script setup></script>

<template>
    <div class="result">
        <slot name="actions"></slot>
        <div class="category-labels" data-testid="results-item-categories">
            <slot name="labels"></slot>
        </div>
        <div class="result__context" data-testid="results-item-context">
            <slot name="context"></slot>
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
