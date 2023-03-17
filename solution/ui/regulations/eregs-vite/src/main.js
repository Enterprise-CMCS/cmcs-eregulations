import Vue from "vue";
import vuetify from "./plugins/vuetify";
import App from "./App.vue";
import router from "./router";

import Clickaway from "./directives/clickaway";

const mountEl = document.querySelector("#vite-app");
Vue.config.devtools = true;
const { customUrl, host } = mountEl.dataset;

Vue.directive("clickaway", Clickaway);

new Vue({
    vuetify,
    router: router({ customUrl, host }),
    render: (h) => h(App, { props: { ...mountEl.dataset } }),
}).$mount("#vite-app");
