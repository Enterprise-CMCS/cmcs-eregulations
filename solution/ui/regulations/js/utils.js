/* eslint-disable */
import _delay from "lodash/delay";
import _get from "lodash/get";

// a promise friendly delay function
function delay(seconds) {
    return new Promise((resolve) => {
        _delay(resolve, seconds * 1000);
    });
}

function parseError(err) {
    console.log(err);
    const errMessage = err.errors
        ? err.errors[Object.keys(err.errors)[0]][0]
        : err.message;
    errMessage && alert(errMessage);

    const message = errMessage;
    try {
        const code = Object.keys(err.errors)[0];
        const status = _get(err, "status");
        const requestId = _get(err, "requestId");
        const error = new Error(message);
        error.code = code;
        error.requestId = requestId;
        error.root = err;
        error.status = status;

        return error;
    } catch {
        return new Error(message);
    }
}

const EventCodes = {
    SetSection: "SetSection",
};

const formatResourceCategories = (resources) => {
    const rawCategories = JSON.parse(
        document.getElementById("categories").textContent
    );

    resources
        .filter((resource) => resource.category.type === "category")
        .forEach((resource) => {
            const existingCategory = rawCategories.find(
                (category) => category.name === resource.category.name
            );

            if (existingCategory) {
                if (!existingCategory.supplemental_content) {
                    existingCategory.supplemental_content = [];
                }
                existingCategory.supplemental_content.push(resource);
            } else {
                const newCategory = JSON.parse(
                    JSON.stringify(resource.category)
                );
                newCategory.supplemental_content = [resource];
                newCategory.sub_categories = [];
                rawCategories.push(newCategory);
            }
        });

    const rawSubCategories = JSON.parse(
        document.getElementById("sub_categories").textContent
    );

    resources
        .filter((resource) => resource.category.type === "subcategory")
        .forEach((resource) => {
            const existingSubCategory = rawSubCategories.find(
                (category) => category.name === resource.category.name
            );

            if (existingSubCategory) {
                if (!existingSubCategory.supplemental_content) {
                    existingSubCategory.supplemental_content = [];
                }
                existingSubCategory.supplemental_content.push(resource);
            } else {
                const newSubCategory = JSON.parse(
                    JSON.stringify(resource.category)
                );
                newSubCategory.supplemental_content = [resource];
                rawSubCategories.push(newSubCategory);
            }
        });
    const categories = rawCategories.map((c) => {
        const category = JSON.parse(JSON.stringify(c));
        category.sub_categories = rawSubCategories.filter(
            (subcategory) => subcategory.parent.id === category.id
        );
        return category;
    });
    categories.sort((a, b) => a.order - b.order);
    categories.forEach((category) => {
        category.sub_categories.sort((a, b) => a.order - b.order);
    });
    return categories;
};

function flattenSubpart(subpart) {
    const result = JSON.parse(JSON.stringify(subpart));
    const subjectGroupSections = subpart.children
        .filter((child) => child.type === "subject_group")
        .flatMap((subjgrp) => subjgrp.children)
        .filter((child) => child.type === "section");

    result.children = result.children
        .concat(subjectGroupSections)
        .filter((child) => child.type === "section");

    return result;
}

const formatDate = (value) => {
    const date = new Date(value);
    const options = {
        year: "numeric",
        month: "long",
        day: "numeric",
        timeZone: "UTC",
    };
    const format = new Intl.DateTimeFormat("en-US", options);

    const formattedDate = format.format(date);
    const splitDate = formattedDate.split(" ");

    if (splitDate[0] && splitDate[0].length > 4) {
        const month = splitDate[0];
        const abbrMonth = month.slice(0, 3);
        splitDate[0] = abbrMonth;
        return splitDate.join(" ");
    }

    return formattedDate;
};

const getQueryParam = (location, key) => {
    const queryParams = new URL(location).searchParams;
    return queryParams.get(key);
};

/**
 * Recursively search through DOM Element and its children and
 * surround strings that match `highlightString` with <mark> tags
 *
 * @param {HTMLElement} element - element to mutate
 * @param {string} highlightString - string to match
 */
function addMarks(element, highlightString) {
    const regex = new RegExp(highlightString, "gi");
    if (element.nodeType === document.TEXT_NODE) {
        // note `nodeValue` vs `innerHTML`
        // nodeValue gives inner text without Vue component markup tags;
        // innerHTML gives text with Vue Component markup tags;
        // Currently there is only the <copy-btn> tag at beginning
        var text = element.nodeValue;
        if (text.toUpperCase().indexOf(highlightString.toUpperCase()) !== -1) {
            const innerHtmlOfParentNode = element.parentNode.innerHTML;
            const indexOfText = innerHtmlOfParentNode.indexOf(text);
            const textToKeep = innerHtmlOfParentNode.slice(0, indexOfText);
            const textToAlter = innerHtmlOfParentNode.slice(indexOfText);
            const newText = textToAlter.replace(
                regex,
                "<mark class='highlight'>$&</mark>"
            );
            element.parentNode.innerHTML = textToKeep + newText;
            return true;
        }
    } else if (element.nodeType === document.ELEMENT_NODE) {
        for (var i = 0; i < element.childNodes.length; i++) {
            if (element.childNodes[i].nodeName !== "MARK") {
                addMarks(element.childNodes[i], highlightString);
            }
        }
    }
}

/**
 * Retrieve comma-separated list of strings from query param in URL
 * and highlight those strings on the page using <mark> tags
 *
 * @param {Location} location - Location object with information about current location of document
 * @param {string} paramKey - name of query parameter containing strings to match and highlight
 */
const highlightText = (location, paramKey) => {
    const textToHighlight = getQueryParam(location, paramKey);
    if (location.hash && textToHighlight) {
        const elementId = location.hash.replace(/^#/, "");
        const targetedSection = document.getElementById(elementId);
        if (targetedSection) {
            const textArr = textToHighlight.split(",");
            textArr.forEach((text) => {
                addMarks(targetedSection, text);
            });
        }
    }
};

export {
    delay,
    EventCodes,
    flattenSubpart,
    formatDate,
    formatResourceCategories,
    getQueryParam,
    highlightText,
    parseError,
};
