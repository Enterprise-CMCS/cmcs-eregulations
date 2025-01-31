<template>
    <li class="dropdown-item">
        <a :href="href" class="dropdown-link">
            <slot />
        </a>
    </li>
</template>

<script>
export default {
    name: "DropdownItem"
};
</script>
