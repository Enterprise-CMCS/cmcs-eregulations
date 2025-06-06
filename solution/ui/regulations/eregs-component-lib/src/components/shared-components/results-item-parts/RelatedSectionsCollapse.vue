<script>
import { inject } from "vue";

const getCollapseName = (doc) =>
    `related citations collapsible ${doc.id ?? doc.node_id}`;

export default { getCollapseName };
</script>

<script setup>
import CollapseButton from "../../CollapseButton.vue";
import Collapsible from "../../Collapsible.vue";
import RelatedSections from "./RelatedSections.vue";

const props = defineProps({
    item: {
        type: Object,
        required: true,
    },
    baseUrl: {
        type: String,
        required: true,
    },
    partsLastUpdated: {
        type: Object,
        required: true,
    },
    collapseName: {
        type: String,
        required: true,
    },
    hasStatuteCitations: {
        type: Boolean,
        required: true,
    },
    hasRegulationCitations: {
        type: Boolean,
        required: true,
    },
});

const homeUrl = inject("homeUrl");
</script>

<template>
    <CollapseButton
        :name="getCollapseName(props.item)"
        state="collapsed"
        class="related-citations__btn--collapse"
    >
        <template #expanded>
            Hide Related Citations
            <i class="fa fa-chevron-up" />
        </template>
        <template #collapsed>
            Show Related Citations
            <i class="fa fa-chevron-down" />
        </template>
    </CollapseButton>
    <Collapsible
        :name="getCollapseName(props.item)"
        state="collapsed"
        class="collapse-content"
        overflow
    >
        <template v-if="props.hasStatuteCitations">
            <RelatedSections
                class="related-statutes"
                :base="homeUrl"
                :item="props.item"
                label="Statutes"
            />
        </template>
        <template v-if="props.hasRegulationCitations">
            <RelatedSections
                class="related-regulations"
                :base="homeUrl"
                :item="props.item"
                :parts-last-updated="props.partsLastUpdated"
                label="Regulations"
            />
        </template>
    </Collapsible>
</template>
