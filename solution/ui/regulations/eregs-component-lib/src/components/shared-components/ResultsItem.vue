<template>
    <div class="result">
        <slot name="actions" />
        <div class="category-labels" data-testid="results-item-categories">
            <slot name="labels" />
        </div>
        <div class="result__context" data-testid="results-item-context">
            <slot name="context" />
        </div>
        <div class="result__link">
            <slot name="link">
                <div style="margin-bottom: -8px" />
            </slot>
        </div>
        <div class="result__snippet">
            <slot name="snippet" />
        </div>
        <slot name="resources-content" />
        <slot name="chips" />
        <slot name="sections" />
    </div>
</template>
