import RelatedRules from "./RelatedRules.js";
import Collapsible from "./Collapsible.js";
import CollapseButton from "./CollapseButton.js";
import SupplementaryContent from "./SupplementaryContent.js";
import CopyBtn from "./CopyBtn.js";
import Vue from "../../node_modules/vue/dist/vue.esm.browser.min.js";
import { goToVersion } from "./go-to-version.js";

Vue.config.devtools = true;

function isElementInViewport(el) {
    var rect = el.getBoundingClientRect();

    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <=
            (window.innerHeight ||
                document.documentElement
                    .clientHeight) /* or $(window).height() */ &&
        rect.right <=
            (window.innerWidth ||
                document.documentElement.clientWidth) /* or $(window).width() */
    );
}

// scroll to anchor to accommodate FF's bad behavior
function onPageShow() {
    // some magic number constants
    // investigate pulling in SCSS variables instead
    const HEADER_HEIGHT = 102;
    const HEADER_HEIGHT_MOBILE = 81;

    // if version select is open, get its height
    // and adjust scrollTo position
    const versionSelectBar = document.getElementsByClassName(
        "view-and-compare"
    );
    const versionSelectHeight = versionSelectBar.length
        ? versionSelectBar[0].offsetHeight
        : 0;

    const elId = window.location.hash;

    if (elId.length > 1) {
        const el = document.getElementById(elId.substr(1));
        if (el) {
            const position = el.getBoundingClientRect();
            const headerHeight =
                window.innerWidth >= 1024
                    ? HEADER_HEIGHT
                    : HEADER_HEIGHT_MOBILE;
            window.scrollTo(
                position.x,
                el.offsetTop - headerHeight - versionSelectHeight
            );
        }
    }
}

function deactivateAllTOCLinks() {
    const active_els = document.querySelectorAll(".menu-section.active");
    for (let active_el of active_els) {
        active_el.classList.remove("active");
    }
}

function getCurrentSectionFromHash() {
    const hash = window.location.hash.substring(1);
    const citations = hash.split("-");
    return citations.slice(0, 2).join("-");
}

function activateTOCLink() {
    deactivateAllTOCLinks();
    const section = getCurrentSectionFromHash();

    const el = document.querySelector(`[data-section-id='${section}']`);
    if (!el) return;

    el.classList.add("active");
    if (!isElementInViewport(el)) {
        el.scrollIntoView();
    }
}

const setResponsiveState = (el) => {
    // left sidebar defaults to collapsed on screens
    // narrower than 1024px
    if (
        el.dataset.stateName === "left-sidebar" &&
        el.dataset.state === "expanded" &&
        window.innerWidth < 1024
    ) {
        el.setAttribute("data-state", "collapsed");
        return;
    }
};

function makeStateful(el) {
    const state_change_target = el.getAttribute("data-state-name");
    const state_change_buttons = document.querySelectorAll(
        `[data-set-state][data-state-name='${state_change_target}']`
    );

    setResponsiveState(el);

    for (const state_change_button of state_change_buttons) {
        state_change_button.addEventListener("click", function () {
            const state = this.getAttribute("data-set-state");
            el.setAttribute("data-state", state);
        });
    }
}

function viewButtonClose() {
    const viewButton = document.querySelector("#view-button");
    if (!viewButton) {
        return;
    }
    viewButton.addEventListener("click", function () {
        if (this.getAttribute("data-state") === "show") {
            // focus on select
            document.querySelector("#view-options").focus();

            this.setAttribute("data-set-state", "close");
        }

        if (this.getAttribute("data-state") === "close") {
            const closeLink = document.querySelector("#close-link");
            closeLink.click();
        }
    });
}

function main() {
    new Vue({
        components: {
            RelatedRules,
            Collapsible,
            CollapseButton,
            SupplementaryContent,
            CopyBtn,
        },
    }).$mount("#vue-app");

    const stateful_elements = document.querySelectorAll("[data-state]");
    for (const el of stateful_elements) {
        makeStateful(el);
    }

    viewButtonClose();
    goToVersion();

    window.addEventListener("hashchange", activateTOCLink);
    activateTOCLink();

    let reset_button = document.getElementById("search-reset");
    if (reset_button) {
        reset_button.addEventListener("click", (event) => {
            document.getElementById("search-field").value = "";
            event.preventDefault();
        });
    }

    window.addEventListener("pageshow", onPageShow);
}

main();
