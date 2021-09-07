export function goToVersion() {
    const select = document.querySelector("#view-options");
    if (!select) {
        return;
    }

    const options = document.querySelectorAll("#view-options [data-url]");
    select.addEventListener("change", function () {
        location.href =
            this.options[this.selectedIndex].dataset.url + location.hash;
    });

    const closeBtn = document.getElementById("close-link");

    // Do not reload page if closing version select bar from latest version;
    // just re-hide version select bar
    closeBtn.addEventListener("click", (e) => {
        if (e.currentTarget.href === location.href) {
            const viewButton = document.querySelector("#view-button");
            viewButton.setAttribute("data-set-state", "show");
            viewButton.setAttribute("data-state", "not-selected");
            const versionSelectBar = document.getElementById(
                "view-and-compare"
            );
            versionSelectBar.setAttribute("data-state", "hide");
        }
    });

    // append current hash to end of closeBtn a href
    // on load and on hashchange
    window.addEventListener("pageshow", () => {
        closeBtn.href = closeBtn.href.split("#")[0] + location.hash;
    });
    window.addEventListener("hashchange", () => {
        closeBtn.href = closeBtn.href.split("#")[0] + location.hash;
    });

    // if not latest version show view div
    const latest_version = options[0].dataset.url;

    if (!location.href.includes(latest_version)) {
        const state_change_target = "view";
        const view_elements = document.querySelectorAll(
            `[data-state][data-state-name='${state_change_target}']`
        );
        for (const el of view_elements) {
            el.setAttribute("data-state", "show");
        }

        // add class to content container for scroll-margin-top
        // when go to version bar is visible
        const contentContainer = document.querySelector(".content");
        contentContainer.classList.add("go-to-version");
    }

    for (const option of options) {
        const url = option.dataset.url;
        if (location.href.includes(url)) {
            option.setAttribute("selected", "");
            break;
        }
    }
}
