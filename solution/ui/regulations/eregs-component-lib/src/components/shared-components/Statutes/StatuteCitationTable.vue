<script setup>
import CopyCitation from "eregsComponentLib/src/components/tooltips/CopyCitation.vue";
import { computed, ref } from "vue";

const props = defineProps({
    citationObj: {
        type: Object,
        required: false,
        default: () => ({}),
    },
    error: {
        type: Boolean,
        required: false,
        default: false,
    },
});

const selectedIndex = ref(null);

const citationArr = computed(() => {
    if (props.error || !props.citationObj) {
        return [];
    }

    return Object.entries(props.citationObj)
        .filter(([key, _value]) => key !== "input")
});

const handleCopyClicked = (payload) => {
    selectedIndex.value = payload.index;
};
</script>

<template>
    <div
        v-if="citationArr.length > 0 || error"
        class="more-info__container citation-links"
    >
        <h3 class="more-info__title">
            Citation Link
        </h3>
        <div
            v-if="error"
            class="more-info__row"
            data-testid="error-row"
        >
            <span class="row__content">
                No citation link found for the provided pattern.
            </span>
        </div>
        <div
            v-for="(item, index) in citationArr"
            :key="item[0]"
            class="more-info__row"
        >
            <div class="copy-btn__container">
                <CopyCitation
                    :formatted-citation="item[0] !== 'link' ? item[1] : null"
                    :link="item[0] === 'link' ? item[1] : null"
                    :action-type="item[0] === 'link' ? 'link' : 'citation'"
                    :index="index"
                    :selected-index="selectedIndex"
                    @copy-clicked="handleCopyClicked"
                />
            </div>
            <div class="row__content">
                <a
                    v-if="item[0] === 'link'"
                    :href="item[1]"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="external"
                >
                    {{ item[1] }}
                </a>
                <span v-else>
                    {{ item[1] }}
                </span>
            </div>
        </div>
    </div>
</template>
