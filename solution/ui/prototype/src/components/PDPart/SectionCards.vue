<template>
    <div>
        <div
            v-for="f in supplemental_content"
            :key="f.name"
            class="card"
        >
            <v-card
                outlined
                elevation="1"
                width="100%"
                class="mx-auto"
            >
                <v-card-subtitle color="#102e43">
                    {{
                        f.category
                    }}
                </v-card-subtitle><v-card-text>
                    <a :href="f.url">
                        {{ f.description }}
                    </a>
                </v-card-text>
                <v-card-actions>
                    <v-btn
                        color="#5B616B"
                        text
                    >
                        Relevant Regulations
                    </v-btn>

                    <v-spacer />

                    <v-btn
                        color="#5B616B"
                        icon
                        @click="toggleLocations(f)"
                    >
                        <v-icon>
                            {{
                                show === f.url ? "mdi-chevron-up" : "mdi-chevron-down"
                            }}
                        </v-icon>
                    </v-btn>
                </v-card-actions>

                <v-expand-transition>
                    <div v-show="show === f.url">
                        <v-divider />
                        <v-card-text>
                            {{ f.locations }}
                        </v-card-text>
                    </div>
                </v-expand-transition>
            </v-card>
        </div>
    </div>
</template>

<script>

export default {
    name: "SectionCards",
    props: {
        title: { type: String },
        part: { type: String },
        supList: {type: Array},
    },
    data: () => ({
        show: false,
    }),
    computed: {
      supplemental_content(){
        const content = []
        this.supList.forEach( category => {
              category
                  .supplemental_content
                  .map(c => {
                    c.category = category.name
                    return c
                  })
                  .forEach(c => content.push(c));
              category
                  .sub_categories.forEach( subCategory => {
                    subCategory
                    .supplemental_content
                    .map(c => {
                      c.category = subCategory.name
                      return c
                    })
                    .forEach(c => content.push(c))
              })
            })
        console.log(content)
        return content
      }
    },
    methods:{
      toggleLocations(f){
        this.show = this.show === f.url ? "":f.url
      },
    }
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