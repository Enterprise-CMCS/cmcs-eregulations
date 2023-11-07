// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })
import "@testing-library/cypress/add-commands";
import "cypress-axe";
import "cypress-plugin-tab";

import { getResources, getSearchGovResources } from "./api-request-commands";
import {
    checkBlockingModal,
    checkFlashBanner,
    clickHeaderLink,
    goHome,
} from "./common-commands/header";
import {
    jumpToRegulationPart,
    jumpToRegulationPartSection,
} from "./common-commands/jumpTo";
import { eregsLogin, setUserGroup } from "./common-commands/login";
import { clickStatuteLink } from "./common-commands/statutes";
import { checkLinkRel } from "./common-commands/checkLinks";
import { validateSchema } from "./validate-schema-command";

Cypress.Commands.add("checkBlockingModal", checkBlockingModal);
Cypress.Commands.add("checkFlashBanner", checkFlashBanner);
Cypress.Commands.add("checkLinkRel", checkLinkRel);
Cypress.Commands.add("clickHeaderLink", clickHeaderLink);
Cypress.Commands.add("clickStatuteLink", clickStatuteLink);
Cypress.Commands.add("getResources", getResources);
Cypress.Commands.add("getSearchGovResources", getSearchGovResources);
Cypress.Commands.add("goHome", goHome);
Cypress.Commands.add("jumpToRegulationPart", jumpToRegulationPart);
Cypress.Commands.add(
    "jumpToRegulationPartSection",
    jumpToRegulationPartSection
);
Cypress.Commands.add("eregsLogin", eregsLogin);
Cypress.Commands.add("setUserGroup", setUserGroup);
Cypress.Commands.add("validateSchema", validateSchema);

// Print cypress-axe violations to the terminal
function printA11yViolations(violations) {
    cy.task(
        "table",
        violations.map(({ id, impact, description, nodes }) => ({
            impact,
            description: `${description} (${id})`,
            nodes: nodes.length,
        }))
    );
}

Cypress.Commands.add(
    "checkAccessibility",
    {
        prevSubject: "optional",
    },
    (subject, { skipFailures = false } = {}) => {
        cy.injectAxe();
        cy.checkA11y(
            subject,
            { includedImpacts: ["critical", "serious"] },
            printA11yViolations,
            skipFailures
        );
    }
);

Cypress.Commands.add("setCssMedia", (media) => {
    Cypress.automation("remote:debugger:protocol", {
        command: "Emulation.setEmulatedMedia",
        params: {
            media,
        },
    });
});

// https://github.com/cypress-io/cypress/issues/1208
Cypress.Commands.add("clearIndexedDB", async () => {
    const databases = await window.indexedDB.databases();

    await Promise.all(
        databases.map(
            ({ name }) =>
                new Promise((resolve, reject) => {
                    const request = window.indexedDB.deleteDatabase(name);

                    request.addEventListener("success", resolve);
                    // Note: we need to also listen to the "blocked" event
                    // (and resolve the promise) due to https://stackoverflow.com/a/35141818
                    request.addEventListener("blocked", resolve);
                    request.addEventListener("error", reject);
                })
        )
    );
});
