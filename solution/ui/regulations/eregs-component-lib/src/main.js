import { createApp } from "vue";
import vuetify from "./plugins/vuetify";

import {
    AccessLink,
    ActionBtn,
    CollapseButton,
    Collapsible,
    CopyCitation,
    DocTypeLabel,
    GovInfoLinks,
    HeaderComponent,
    HeaderLinks,
    HeaderSearch,
    SignInCta,
    SignInLink,
    IndicatorLabel,
    InternalDocsContainer,
    JumpTo,
    CategoryLabel,
    LastParserSuccessDate,
    LeftNavCollapse,
    RecentChangesContainer,
    RecentResources,
    RelatedRule,
    RelatedRuleList,
    RelatedSectionsCollapse,
    ShowMoreButton,
    SimpleSpinner,
    SupplementalContent,
    SupplementalContentCategory,
    SupplementalContentList,
    SupplementalContentObject,
    TableComponent,
    Toc,
    TocContainer,
    TocPart,
    TocSubchapter,
    TocTitle,
    TooltipContainer,
    HeaderUserWidget,
    ViewResourcesLink,
} from "../dist/eregs-components.es";

import { goToVersion } from "./go-to-version";
import {
    highlightText,
    getCurrentSectionFromHash,
    getQueryParam,
    scrollToElement,
} from "utilities/utils";

import Clickaway from "directives/clickaway";
import SanitizeHtml from "directives/sanitizeHtml";

const customElementTags = [
    "su",
    "fp",
    "fp-1",
    "fp1-2",
    "fp-2",
    "fp-3",
    "fp-4",
    "fp-5",
    "fp-6",
];

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

function activateTOCLink() {
    deactivateAllTOCLinks();
    const section = getCurrentSectionFromHash(window.location.hash);

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

    const app = createApp({
        components: {
            AccessLink,
            ActionBtn,
            CollapseButton,
            Collapsible,
            CopyCitation,
            DocTypeLabel,
            GovInfoLinks,
            HeaderComponent,
            HeaderLinks,
            HeaderSearch,
            SignInCta,
            SignInLink,
            IndicatorLabel,
            InternalDocsContainer,
            JumpTo,
            CategoryLabel,
            LastParserSuccessDate,
            LeftNavCollapse,
            RecentChangesContainer,
            RecentResources,
            RelatedRule,
            RelatedRuleList,
            RelatedSectionsCollapse,
            ShowMoreButton,
            SimpleSpinner,
            SupplementalContent,
            SupplementalContentCategory,
            SupplementalContentList,
            SupplementalContentObject,
            TableComponent,
            Toc,
            TocContainer,
            TocPart,
            TocSubchapter,
            TocTitle,
            TooltipContainer,
            HeaderUserWidget,
            ViewResourcesLink,
        },
    });

    app.config.compilerOptions.isCustomElement = (tag) =>
        customElementTags.includes(tag);

    app.use(vuetify);

    app.directive("clickaway", Clickaway);
    app.directive("sanitize-html", SanitizeHtml);

    app.mount("#vue-app");

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
