<script setup>
import RelatedRegulationLink from "./RelatedRegulationLink.vue";
import RelatedStatuteLink from "./RelatedStatuteLink.vue";

const props = defineProps({
    base: {
        type: String,
        required: true,
    },
    item: {
        type: Object,
        required: true,
    },
    label: {
        type: String,
        default: "Related Section",
    },
    partsLastUpdated: {
        type: Object,
        default: () => {},
    },
});

let groupedCitations = [];

if (props.label === "Regulations") {
    const citations = props.item.cfr_citations
        ? props.item.cfr_citations.filter((citation) => {
            const { part } = citation;
            return props.partsLastUpdated[part];
        })
        : [];

    const mappedCitations = citations.map((citation) => {
        citation.title = `${citation.title} CFR`;
        return citation;
    });

    groupedCitations = Object.groupBy(mappedCitations, (citation) => {
        return citation.title;
    });
} else {
    const actCitations = props.item.act_citations
        .map((citation) => {
            citation.title = citation.act;
            return citation;
        });
    const groupedActCitations = Object.groupBy(actCitations, citation => {
        return citation.title;
    });

    const uscCitations = props.item.usc_citations
        .map((citation) => {
            citation.title = `${citation.title} U.S.C.`;
            return citation;
        });
    const groupedUscCitations = Object.groupBy(uscCitations, citation => {
        return citation.title;
    });

    groupedCitations = {
        ...groupedActCitations,
        ...groupedUscCitations,
    };
}

</script>

<template>
    <div class="related-sections">
        <span class="related-sections-title"> {{ label }}: </span>
        <template
            v-for="(citations, title, i) in groupedCitations"
            :key="title + i"
        >
            <span class="title__span">
                {{ title }}
            </span>
            <span
                v-if="citations.length > 1"
                :key="i + title"
                class="section-sign"
            > §§ </span>
            <span
                v-else
                :key="i + title + i"
                class="section-sign"
            > § </span>
            <template
                v-for="(citation, j) in citations"
                :key="i + 'key' + j"
            >
                <span class="related-section-link">
                    <RelatedRegulationLink
                        v-if="props.label === 'Regulations'"
                        :citation="citation"
                        :base="base"
                    />
                    <RelatedStatuteLink
                        v-else
                        v-bind="citation"
                    />
                    <span v-if="j + 1 != citations.length">, </span>
                </span>
            </template>
            <span
                v-if="i + 1 != Object.keys(groupedCitations).length"
                :key="i + title + i"
                class="pipe-separator"
            >; </span>
        </template>
    </div>
</template>

<style></style>
