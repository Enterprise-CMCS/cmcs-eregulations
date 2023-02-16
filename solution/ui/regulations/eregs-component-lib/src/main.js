import Vue from "vue/dist/vue.esm.browser.min";

import { TestComponent } from "../dist/eregs-components.es"

Vue.config.devtools = true;

function main() {
    new Vue({
        components: {
            TestComponent,
        },
    }).$mount("#vue-app");
}

main();
