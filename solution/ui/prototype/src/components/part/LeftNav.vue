<template>
    <v-navigation-drawer
        v-model="drawer"

        absolute
        left
        permanent
        mini-variant-width="40"
        width="458"
        style="padding-top: 75px; background-color:#254C68"
    >
        <v-list-item v-if="mini" class="px-2">
            <v-btn
                icon
                @click.stop="mini = false"
            >
                <v-icon style="color:#CCF2FF">mdi-menu</v-icon>
            </v-btn>
        </v-list-item>

        <div v-if="!mini" class="leftNav-body">
            <v-tabs
                fixed-tabs
                v-model="tab"
            >
                <v-tab
                    v-for="title in toc"
                    :key="title.label_level"
                >
                    {{title.label_level}}
                </v-tab>
            </v-tabs>

            <v-tabs-items v-model="tab">
                <v-tab-item
                    v-for="title in toc"
                    :key="title.label_level"
                >
                    <div class="leftNav-item">
                        <div class="leftNav-header">
                            <div class="header">{{ title.label }}</div>
                            <div class="subheader">{{ title.children[0].label }}</div>
                        </div>
                        <ul class="leftNav-list">
                            <li v-for="subChapter in title.children[0].children">
                                <div class="leftNav-subchapter">{{ subChapter.label }}</div>
                                <ul class="leftNav-list leftNav-sectionlist">
                                      <li v-for="part in subChapter.children">
                                        <div style="width:100%"><v-icon style="float:right; color:#CCF2FF">mdi-chevron-right</v-icon> {{ part.label }} </div>
                                      </li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                </v-tab-item>
            </v-tabs-items>
        </div>
    </v-navigation-drawer>
</template>

<script>
import InlineLoader from "@/components/InlineLoader.vue";
import {getTOC} from "@/utilities/api";

export default {
    components: {
        InlineLoader,
    },

    name: "LeftNav",
    data () {
      return {
        drawer: true,
        tab: null,
        mini: false,
        toc: []
      }
    },
    props: {},
    async created() {
      this.toc = await getTOC()
    },
    computed: {},
};
</script>

<style lang="scss">
.leftNav-body{
  color: white;
  background-color:#254C68;
  font-family: "Open Sans"
}
.leftNav-item{
  color: white;
  background-color:#254C68;
  padding:5px;
}
.leftNav-header{
  font-size:20px;
  line-height: 22px;
  padding: 16px;
}
.leftNav-header .header{
    font-size: 22px;
    font-weight:bold;
}
.leftNav-header .subheader{
    font-size: 14px;
}
.leftNav-list{
  list-style: none;
}
.leftNav-subchapter{
  font-size:16px;
  font-weight: bold;
}
.leftNav-sectionlist{
  color: #CCF2FF;
  font-size:14px;
  padding: 8px;
}
</style>
