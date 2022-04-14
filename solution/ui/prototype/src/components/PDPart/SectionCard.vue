<template>
    <v-card
        outlined
        elevation="1"
        width="100%"
        class="mx-auto"
        :key="f.url"
    >
        <v-card-subtitle color="#102e43">
            {{
                f.category
            }}
        </v-card-subtitle><v-card-text :class="$style['search-highlight']">
            <a :href="f.url" v-html="f.descriptionHeadline || f.description" />
        </v-card-text>
        <v-card-actions
          @click="showLocation = !showLocation"
        >
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
            >
                <v-icon>
                    {{
                        showLocation ? "mdi-chevron-up" : "mdi-chevron-down"
                    }}
                </v-icon>
            </v-btn>
        </v-card-actions>

        <v-expand-transition>
            <div v-show="showLocation">
                <v-divider />
                <v-card-text>
                    <div v-if="subpartLocations.length > 0">
                        This resource is linked to the following subparts:
                        <ul>
                            <li v-for="location in subpartLocations">
                                Part
                                <router-link
                                    :to="{
                                        name: 'PDpart-subPart',
                                        params: {
                                            title: location.title,
                                            part:location.part,
                                            subPart: 'subPart-' + location.display_name[location.display_name.length -1]
                                        },
                                    }"
                                >
                                    {{ location.display_name.slice(3,) }}
                                </router-link>
                            </li>
                        </ul>
                    </div>
                    <div v-if="sectionLocations">
                        This resource is linked to the following sections:
                        <ul>
                            <li v-for="(locations, part) in sectionLocations">
                                Within <a>Part {{ part }}</a>
                                <ul>
                                    <li>
                                        §§ <span v-for="location in locations">
                              
                                            <router-link
                                                :to="{
                                                    name: 'PDpart',
                                                    params: {
                                                        title: location.title,
                                                        part: location.part,
                                                    },
                                                }"
                                            >
                                                {{ location.display_name.slice(3,) }}
                                            </router-link>
                                    &nbsp;
                                        </span>
                                    </li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                </v-card-text>
            </div>
        </v-expand-transition>
    </v-card>
</template>

<script>
export default {
  name: "SectionCard",
  props: {
    f: {type: Object},
    usingSearch: {type: Boolean},
  },
  data: () => ({
    showLocation: false,
  }),
  computed:{
    subpartLocations(){
      const results = []
      this.f.locations.forEach( l => {
        if (l.display_name.indexOf('Subpart') > 0) {
            results.push(l)
        }
      })
      return results
    },
    sectionLocations (){
      const results = {}
      this.f.locations.forEach( l => {
        if (l.display_name.indexOf('Subpart') < 0) {
          if (results[l.part]) {
            results[l.part].push(l)
          } else {
            results[l.part] = [l]
          }
        }
      })
      return results
    },
  }
}
</script>

<style module>
.search-highlight span {
    font-style: italic;
    font-weight: bold;
}
</style>