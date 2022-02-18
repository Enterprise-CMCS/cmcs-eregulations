<template>
    <section
        aria-labelledby="{{ node.label }}-title"
        tabindex="-1"
        id="{{ node.label }}"
        class="appendix-section"
    >
        <h2 class="section-title" id="{{ node.label }}-title">
            {% appendix_formatter cfr_title node.label as formatted_citation %}
            {% include "regulations/partials/copy-btn.html" with
            title=node.label btn_type="icon"
            formatted_citation=formatted_citation %}
            {{ node.title }}
        </h2>

        <div class="paragraphs">
            {{ node.text }}
        </div>
    </section>
</template>

<script>
export default {
    name: "Appendix",

    props: {
        node: {
            type: Object,
            required: true
        }
    }
};
</script>

<style></style>
