<template>
    <div
        :class="[mini ? 'mini': 'maxi']"
        class="left-nav"
    >
        <v-btn
            v-if="mini"
            icon
            @click.stop="mini = !mini"
            style="color:#CCF2FF; padding: 10px"
        >
            <v-icon>
                mdi-menu
            </v-icon>
        </v-btn>
        <v-btn
            v-else
            icon
            style="float:right; padding:5px; color:#CCF2FF"
            @click.stop="mini = !mini"
        >
            <v-icon>
                mdi-close
            </v-icon>
        </v-btn>

        <div
            v-if="!mini"
            class="leftNav-body"
        >
            <v-tabs
                v-model="tab"
                background-color="#254C68"
                color="#FFF"
            >
                <v-tab
                    v-for="title in toc"
                    :key="title.label_level"
                    style="color:#FFF"
                >
                    {{ title.label_level }}
                </v-tab>
            </v-tabs>
            <v-divider style="border-color:#046791"/>
            <v-tabs-items v-model="tab">
                <v-tab-item
                    v-for="title in toc"
                    :key="title.label_level"
                >
                    <div class="leftNav-item">
                        <div class="leftNav-header">
                            <div class="header">
                                {{ title.label }}
                            </div>
                            <div class="subheader">
                                {{ title.children[0].label }}
                            </div>
                        </div>
                        <ul class="leftNav-list">
                            <li v-for="subChapter in title.children[0].children">
                                <div class="leftNav-subchapter">
                                    {{ subChapter.label }}
                                </div>
                                <ul class="leftNav-list leftNav-sectionlist">
                                    <li v-for="part in subChapter.children">
                                        <div style="width:100%; padding:6px; display:flex; justify-content: space-between; align-items:center">
                                            <div>{{ part.label }} </div>
                                            <div>
                                                <v-icon style="float:right; color:#CCF2FF">
                                                    mdi-chevron-right
                                                </v-icon>
                                            </div>
                                        </div>
                                    </li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                </v-tab-item>
            </v-tabs-items>
        </div>
    </div>
</template>

<script>
import InlineLoader from "@/components/InlineLoader.vue";
import {getTOC} from "@/utilities/api";

export default {

    name: "LeftNav",
    components: {
        InlineLoader,
    },
    props: {},
    data () {
      return {
        drawer: true,
        tab: null,
        mini: true,
        toc: []
      }
    },
    computed: {},
    async created() {
      this.toc = await getTOC()
    },
};
</script>

<style lang="scss">
.mini{
  width: 60px;
}
.maxi{
  width: 450px;
}
.left-nav{
  color: white;
  background-color:#254C68;
  font-family: "Open Sans";
  height: 100%;
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
