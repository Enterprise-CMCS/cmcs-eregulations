import Vue from "vue";
import vuetify from "./plugins/vuetify";
import App from "./App.vue";
import router from "./router";

new Vue({
    vuetify,
    router,
    render: (h) => h(App),
}).$mount("#vite-app");
