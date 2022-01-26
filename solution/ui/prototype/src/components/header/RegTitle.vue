<template>
    <div class="reg-title" v-if="part">
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
export default {};
</script>

<style></style>
