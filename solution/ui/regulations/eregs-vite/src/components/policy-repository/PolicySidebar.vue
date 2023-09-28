<template>
    <div class="sidebar__filters">
        <slot name="title">
            <h2>Find Policy Documents</h2>
        </slot>
        <div class="sidebar-filters__container">
            <slot name="selections">
            </slot>
            <slot name="search">
            </slot>
            <slot name="filters"></slot>
        </div>
    </div>
</template>
