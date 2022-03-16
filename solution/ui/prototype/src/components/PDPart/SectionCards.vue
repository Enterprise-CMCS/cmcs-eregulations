<template>
    <div>
        <div v-for="content in supList" :key="content.name">
            <div v-for="c in content.sub_categories" :key="c.name">
                <div v-for="f in c.supplemental_content" :key="f.name" class = "card">
                    <v-card outlined elevation="1" width="100%" class="mx-auto"
                        ><v-card-subtitle color="#102e43">{{
                            content.name
                        }}</v-card-subtitle
                        ><v-card-text
                            ><a v-bind:href="f.url">
                                {{ f.description }}
                            </a></v-card-text
                        >
                        <v-card-actions>
                            <v-btn color="#5B616B" text>
                                Relevant Regulations
                            </v-btn>

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
                                    I'm a thing. But, like most politicians, he
                                    promised more than he could deliver. You
                                    won't have time for sleeping, soldier, not
                                    with all the bed making you'll be doing.
                                    Then we'll go with that data file! Hey, you
                                    add a one and two zeros to that or we walk!
                                    You're going to do his laundry? I've got to
                                    find a way to escape.
                                </v-card-text>
                            </div>
                        </v-expand-transition></v-card
                    >
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { getSupplementalContentNew } from "@/utilities/api";

export default {
    name: "SectionCards",
    data: () => ({
        show: false,
        supList: null
    }),
    props: {
        title: { type: String },
        part: { type: String },
        supList: {type: Array},
    },
};
</script>

<style >
.theme--light.v-card > .v-card__subtitle {
    font-size: 11px;
    font-weight: bold;
    color: #102e43;
}
.theme--light.v-card > .v-card__text {
    color: #046791;
}
.v-btn > .v-btn__content {
    font-size: 12px;
}
.v-card__text {
    width: 95%;
}
.card{
    padding-bottom: 10px;
}
</style>