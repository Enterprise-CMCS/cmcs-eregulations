<template>
    <div
        v-if="part"
        class="reg-title"
    >
        <a href="{% url 'regulation_landing_view' title reg_part %}">
            <strong>{{ title }} CFR Part {{ part }}</strong>
            <span class="header-part-name">
                {% if part_label %} - {{ part_label }}
                {% endif %}
            </span>
        </a>
    </div>
</template>

<script>
export default {
    name: "RegTitle",

    props: {
        part: {
            type: Boolean,
            default: false,
        },
    },
};
</script>

<style></style>
