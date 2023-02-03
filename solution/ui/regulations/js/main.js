import Vue from "vue/dist/vue.esm.browser.min.js";

import RelatedRules from "../dist/RelatedRules";
import Collapsible from "../dist/Collapsible";
import CollapseButton from "../dist/CollapseButton";
import SupplementalContent from "../dist/SupplementalContent";
import TooltipContainer from "../dist/TooltipContainer";
import PrintBtn from "../dist/PrintBtn";
import TableComponent from "../dist/TableComponent";
import ViewResourcesLink from "../dist/ViewResourcesLink";
import RecentChangesContainer from "../dist/RecentChangesContainer";
import LastParserSuccessDate from "../dist/LastParserSuccessDate";
import BlockingModal from "../dist/BlockingModal";
import BlockingModalTrigger from "../dist/BlockingModalTrigger";
import FlashBanner from "../dist/FlashBanner";
import IFrameContainer from "../dist/IFrameContainer";
import CopyCitation from "../dist/CopyCitation";
import GovInfoLinks from "../dist/GovInfoLinks";
// #### HYGEN IMPORT INSERTION POINT DO NOT REMOVE ####

import { goToVersion } from "./go-to-version";
import { highlightText, getQueryParam, scrollToElement } from "./utils";

Vue.config.devtools = true;

function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();

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
    // some magic number constants to scroll to top
    // with room for sticky header and some breathing room for content
    // investigate pulling in SCSS variables instead
    const HEADER_HEIGHT = 102;
    const HEADER_HEIGHT_MOBILE = 81;

    const elId = window.location.hash;
    const hasHash = elId.length > 1;
    const isHighlighted = Boolean(getQueryParam(window.location, "highlight"));

    if (hasHash || isHighlighted) {
        // if version select is open, get its height
        // and adjust scrollTo position
        const versionSelectBar = document.getElementsByClassName(
            "view-and-compare"
        );
        const versionSelectHeight = versionSelectBar.length
            ? versionSelectBar[0].offsetHeight
            : 0;

        const headerHeight =
            window.innerWidth >= 1024 ? HEADER_HEIGHT : HEADER_HEIGHT_MOBILE;

        const offsetPx = headerHeight - versionSelectHeight;

        if (isHighlighted) {
            const highlightedEls = document.getElementsByClassName("highlight");
            const highlightedEl = highlightedEls[0];
            if (highlightedEl) {
                scrollToElement(highlightedEl, offsetPx);
            }
        } else if (hasHash) {
            const el = document.getElementById(elId.substr(1));
            if (el) {
                scrollToElement(el, offsetPx);
            }
        }
    }
}

function deactivateAllTOCLinks() {
    const activeEls = document.querySelectorAll(".menu-section.active");
    activeEls.forEach((el) => {
        el.classList.remove("active");
    });
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
    }
};

function makeStateful(el) {
    const stateChangeTarget = el.getAttribute("data-state-name");
    const stateChangeButtons = document.querySelectorAll(
        `[data-set-state][data-state-name='${stateChangeTarget}']`
    );

    setResponsiveState(el);

    stateChangeButtons.forEach((btn) => {
        btn.addEventListener("click", (event) => {
            const state = event.currentTarget.getAttribute("data-set-state");
            el.setAttribute("data-state", state);
        });
    });
}

function viewButtonClose() {
    const viewButton = document.querySelector("#view-button");

    if (!viewButton) {
        return;
    }

    viewButton.addEventListener("click", (event) => {
        if (event.currentTarget.getAttribute("data-state") === "show") {
            // focus on select
            document.querySelector("#view-options").focus();

            event.currentTarget.setAttribute("data-set-state", "close");
        }

        if (event.currentTarget.getAttribute("data-state") === "close") {
            const closeLink = document.querySelector("#close-link");
            closeLink.click();
        }
    });
}

function main() {
    // Must be first, mutates DOM
    highlightText(window.location, "highlight");

    new Vue({
        components: {
            RelatedRules,
            Collapsible,
            CollapseButton,
            SupplementalContent,
            TooltipContainer,
            TableComponent,
            PrintBtn,
            ViewResourcesLink,
            RecentChangesContainer,
            LastParserSuccessDate,
            BlockingModal,
            BlockingModalTrigger,
            FlashBanner,
            IFrameContainer,
            CopyCitation,
            GovInfoLinks,
            // #### HYGEN COMPONENT INSERTION POINT DO NOT REMOVE ####
        },
    }).$mount("#vue-app");

    const statefulElements = document.querySelectorAll("[data-state]");
    statefulElements.forEach((el) => {
        makeStateful(el);
    });

    viewButtonClose();
    goToVersion();

    window.addEventListener("hashchange", activateTOCLink);
    activateTOCLink();

    const resetButton = document.getElementById("search-reset");
    if (resetButton) {
        resetButton.addEventListener("click", (event) => {
            document.getElementById("search-field").value = "";
            event.preventDefault();
        });
    }

    window.addEventListener("pageshow", onPageShow);
}

main();
