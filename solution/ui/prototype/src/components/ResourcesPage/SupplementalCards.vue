<template>
    <div class="supplement-cards">
        <v-card>
            <v-card-subtitle
                >{{ content.category }}
                {{ content.subcategory }}</v-card-subtitle
            >
            <v-card-text>{{ content.description }}</v-card-text>
            <v-card-actions>
                <v-btn color="#5B616B" text> Relevant Regulations </v-btn>

                <v-spacer></v-spacer>

                <v-btn color="#5B616B" icon @click="show = !show">
                    <v-icon>{{
                        show ? "mdi-chevron-up" : "mdi-chevron-down"
                    }}</v-icon>
                </v-btn>
            </v-card-actions>

            <v-expand-transition>
                <div v-show="show">
                    <v-divider></v-divider>

                    <v-card-text>
                        I'm a thing. But, like most politicians, he promised
                        more than he could deliver. You won't have time for
                        sleeping, soldier, not with all the bed making you'll be
                        doing. Then we'll go with that data file! Hey, you add a
                        one and two zeros to that or we walk! You're going to do
                        his laundry? I've got to find a way to escape.
                    </v-card-text>
                </div>
            </v-expand-transition>
        </v-card>
    </div>
</template>
<script>
export default {
    name: "SupplementalCards",
    props: ["content"],
    data: () => ({
        show: false,
    }),
};
</script>
<style scoped>
.supplement-cards {
    padding-bottom: 10px;
}
</style>