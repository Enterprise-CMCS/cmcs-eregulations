<template>
    <v-list class="subpart-list">
        <v-list-item
            v-for="item in listItems"
            :key="item.part + item.identifier"
            :data-value="item.part + '-' + item.identifier"
            class="subpart-list-item"
            @click="clickMethod"
        >
            <div>
                <span class="subpart-letter"
                    >Subpart {{ item.identifier }}</span
                >
                <span class="subpart-range">
                    {{ item.range | formatRange }}</span
                >
            </div>
            <div class="subpart-text">
                {{ item.label | descriptionOnly }}
            </div>
        </v-list-item>
    </v-list>
</template>

<script>
import _isEmpty from "lodash/isEmpty";

export default {
    name: "SubpartList",

    props: {
        filterEmitter: {
            type: Function,
            required: true,
        },
        listItems: {
            type: Array,
            required: true,
        },
        listId: {
            type: String,
            default: "",
        },
    },

    methods: {
        clickMethod(e) {
            this.filterEmitter({
                scope: "subpart",
                selectedIdentifier: e.currentTarget.dataset.value,
            });
        },
    },

    filters: {
        descriptionOnly(value) {
            return value.substring(value.indexOf("-") + 1);
        },
        formatRange(array) {
            if (_isEmpty(array)) return "";
            return `(${array.join(" - ")})`;
        },
    },
};
</script>

<style lang="scss">
.subpart-list-item {
    display: inline-block;
    min-height: unset;
    padding-top: 5px;
    padding-bottom: 5px;
    font-size: 14px;

    .subpart-letter,
    .subpart-range {
        color: $dark_gray;
    }

    .subpart-range {
        font-size: 12px;
    }

    .subpart-text {
        color: $mid_gray;
    }
}
</style>
