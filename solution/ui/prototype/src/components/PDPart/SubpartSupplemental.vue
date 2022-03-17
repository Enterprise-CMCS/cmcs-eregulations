<template>
    <div>
        <supplemental-content-category
            v-for="category in supList"
            :key="category.name"
            :name="category.name"
            :description="category.description"
            :supplemental_content="category.supplemental_content"
            :sub_categories="category.sub_categories"
            :isFetching="true"
        >
        </supplemental-content-category>
    </div>
</template>
<script>
import { getSupplementalContentNew } from "@/utilities/api";
import SupplementalContentCategory from "../../../../regulations/js/src/components/SupplementalContentCategory.vue";

export default {
    name: "SubpartSupplement",
    props: {
        title: { type: String },
        part: { type: String },
        subpart: { type: String },
    },
    data() {
        return {
            supList: null,
        };
    },
    components: {
        getSupplementalContentNew,
        SupplementalContentCategory,
    },
    async created() {
        try {
            this.supList = await getSupplementalContentNew(
                this.title,
                this.part,
                [],
                [this.subpart]
            );
        } catch (error) {
            console.error(error);
        } finally {
            console.log(this.supList);
        }
    },
};
</script>
