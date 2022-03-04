<template>
    <v-card outlined elevation="5" width="100%" class="mx-auto"
        ><v-card-subtitle color="#102e43">{{name}}</v-card-subtitle
        ><v-card-text>{{description}}</v-card-text>
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
                    I'm a thing. But, like most politicians, he promised more
                    than he could deliver. You won't have time for sleeping,
                    soldier, not with all the bed making you'll be doing. Then
                    we'll go with that data file! Hey, you add a one and two
                    zeros to that or we walk! You're going to do his laundry?
                    I've got to find a way to escape.
                </v-card-text>
            </div>
        </v-expand-transition></v-card
    >
</template>

<script>
export default {
    name: "Section Cards",
    data: () => ({
        show: false,
    }),
    props: {
        name: { type: String },
        description: { type: String },
        relevantregs: {type: String},
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
.v-card__text{
    width: 95%;
}

</style>