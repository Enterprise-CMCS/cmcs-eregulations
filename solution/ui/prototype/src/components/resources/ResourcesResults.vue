<template>
    <div class="resources-results">
        <div class="resource-item">
            <template v-for="(item, idx) in sortedContent">
                <span v-if="item.category">{{ item.category }} </span>
                <span v-if="item.sub_category">{{ item.sub_category }}</span>
                <span>Index: {{ idx }}</span>
                <SupplementalContentObject
                    :key="item.created_at"
                    :name="item.name"
                    :description="item.description"
                    :date="item.date"
                    :url="item.url"
                />
            </template>
        </div>
    </div>
</template>

<script>
import SupplementalContentObject from "legacy/js/src/components/SupplementalContentObject.vue";

export default {
    name: "ResourcesResults",

    components: {
        SupplementalContentObject,
    },

    props: {
        content: {
            type: Array,
            required: false,
        },
    },

    beforeCreate() {},

    created() {},

    beforeMount() {},

    mounted() {},

    beforeUpdate() {},

    updated() {},

    beforeDestroy() {},

    destroyed() {},

    data() {
        return {
            dataProp: "value",
        };
    },

    computed: {
        sortedContent() {
            return this.content
                .filter((category) => {
                    return (
                        category.supplemental_content?.length ||
                        category.sub_categories?.length
                    );
                })
                .flatMap((category) => {
                    const returnArr = [];
                    if (category.sub_categories?.length) {
                        category.sub_categories.forEach(sub_category => {
                            sub_category.supplemental_content.forEach((item) => {
                                item.category = category.name;
                                item.sub_category = sub_category.name;
                                returnArr.push(item);
                            })
                        })
                    } else {
                        category.supplemental_content.forEach((item) => {
                            item.category = category.name;
                            returnArr.push(item);
                        });
                    }

                    return returnArr;
                });
        },
    },

    methods: {
        methodName() {
            console.log("method has been invoked");
        },
    },

    watch: {
        content: {
            async handler() {
                console.log(this.content);
            },
        },
    },
};
</script>

<style></style>
