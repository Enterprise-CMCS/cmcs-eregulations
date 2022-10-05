import Vue from "vue";
import vuetify from "./plugins/vuetify";
import App from "./App.vue";
import router from "./router";

const mountEl = document.querySelector("#vite-app");
Vue.config.devtools = true;
new Vue({
    vuetify,
    router,
    render: (h) => h(App, { props: { ...mountEl.dataset } }),
}).$mount("#vite-app");
