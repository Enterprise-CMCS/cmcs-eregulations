<script setup>
import CopyCitation from "eregsComponentLib/src/components/tooltips/CopyCitation.vue";
import { computed } from "vue";

const props = defineProps({
    citationObj: {
        type: Object,
        required: true,
    },
});

const citationArr = computed(() => {
    return Object.entries(props.citationObj)
        .filter(([key, _value]) => key !== "input")
});
</script>

<template>
    <div
        v-if="citationArr.length"
        class="more-info__container citation-links"
    >
        <h3 class="more-info__title">
            Citation Link
        </h3>
        <div
            v-for="item in citationArr"
            :key="item[0]"
            class="more-info__row"
        >
            <div class="copy-btn__container">
                <CopyCitation
                    :formatted-citation="item[0] !== 'link' ? item[1] : null"
                    :link="item[0] === 'link' ? item[1] : null"
                    :action-type="item[0] === 'link' ? 'link' : 'citation'"
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
