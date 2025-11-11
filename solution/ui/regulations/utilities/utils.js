import isEmpty from "lodash/isEmpty";
import isNil from "lodash/isNil";
import isString from "lodash/isString";
import lodashDelay from "lodash/delay";
import lodashDifference from "lodash/difference";
import lodashEndsWith from "lodash/endsWith";
import lodashGet from "lodash/get";

import {
    compressToEncodedURIComponent,
    decompressFromEncodedURIComponent,
} from "lz-string";

const EventCodes = {
    SetSection: "SetSection",
    ClearSections: "ClearSections",
};

const COMPRESSION_PREFIX = ".!~";
const COMPRESSION_INDEX = COMPRESSION_PREFIX.length;

const MAX_QUERY_LENGTH = 7500;
const SEARCH_STRING_COMPRESSION_THRESHOLD = 200;
const SEARCH_STRING_TRUNCATE_THRESHOLD = 1000;

const DOCUMENT_TYPES = ["regulations", "external", "internal"];

const DOCUMENT_TYPES_MAP = {
    external: "Public",
    federal_register_link: "Public",
    public_link: "Public",
    reg_text: "Public",
    internal: "Internal",
    internal_file: "Internal",
    internal_link: "Internal",
    regulations: "Regulations",
};

const SUFFIX_DICT = {
    msg: "Outlook",
};

const INVALID_SUFFIXES = [
    "htm",
    "html",
];

const COUNT_TYPES_MAP = {
    external: "public_resource_count",
    internal: "internal_resource_count",
    regulations: "regulation_text_count",
};

const PARAM_MAP = {
    subjects: "subjects",
    q: "q",
    page: "page",
    categories: "categories",
    intcategories: "categories",
    sort: "sort",
};

/**
 * Validation dictionary for query params to ensure that only valid values are
 * passed to the API.
 * @type {Object}
 * @property {function} subjects - Validates that the subject is a number
 * @property {function} q - Validates that the query is a string or undefined.  We need to allow undefined because Vue Router can return undefined if the query param is not present.
 * @property {function} type - Validates that the type is either "all" or a comma-separated string of valid document types
 * @property {function} page - Validates that the page is a number
 * @property {function} categories - Validates that the category is a number
 * @property {function} intcategories - Validates that the internal category is a number
 * @property {function} sort - Validates that the sort is either "date" or "-date"
 */
const PARAM_VALIDATION_DICT = {
    subjects: (subject) =>
        !Number.isNaN(parseInt(subject, 10)) && !Number.isNaN(Number(subject)),
    q: (query) => query === undefined || query.length > 0,
    type: (type) => {
        if (type === "all") return true;
        if (isString(type)) {
            const typeArray = type.split(",");
            return typeArray.every((t) => DOCUMENT_TYPES.includes(t));
        }
        return false;
    },
    page: (page) => !Number.isNaN(parseInt(page, 10)),
    categories: (category) => !Number.isNaN(parseInt(category, 10)),
    intcategories: (category) => !Number.isNaN(parseInt(category, 10)),
    sort: (sort) => ["date", "-date"].includes(sort),
};

/**
 * Dictionary of query parameters to encode before sending to the API.
 * @type {Object}
 * @property {function} q - Encodes the q search string query parameter
 *
 * @example
 * const query = "SMDL #12-002";
 * const encodedQuery = PARAM_ENCODE_DICT.q(query);
 * console.log(encodedQuery); // "SMDL%20%2312-002"
 */
const PARAM_ENCODE_DICT = {
    q: (query) => encodeURIComponent(decompressRouteQuery({ q: query })),
};

/**
 * @param {string} string - data to be compressed
 * @returns {string} - compressed and encoded string suitable for use in a URL query parameter
 * @example
 * const data = "This is a very long search query that needs to be compressed for URL usage.";
 * const compressed = compressQueryString(string);
 * console.log(compressed); // "CoCwlgzgBJUIZQG4FMBOBPKAbA9gOwHMoJk5UBjEKARwFc1MAXEORqPZZAE2kZygBGyKORwBbAA6pkEElygAzHKigBVAEoAZKLQhwCyAHRA"
 */
const compressQueryString = (string) => {
    try {
        return compressToEncodedURIComponent(string);
    } catch (error) {
        console.error("Error compressing query string:", error);
        return "";
    }
};

/**
 * @param {string} compressedStr - compressed and encoded string from URL query parameter
 * @returns {string} - decompressed data
 * @example
 * const compressedStr = "CoCwlgzgBJUIZQG4FMBOBPKAbA9gOwHMoJk5UBjEKARwFc1MAXEORqPZZAE2kZygBGyKORwBbAA6pkEElygAzHKigBVAEoAZKLQhwCyAHRA";
 * const string = decompressQueryString(compressedStr);
 * console.log(string); // "This is a very long search query that needs to be compressed for URL usage."
 */
const decompressQueryString = (compressedStr) => {
    try {
        return decompressFromEncodedURIComponent(compressedStr);
    } catch (error) {
        console.error("Error decompressing query string:", error);
        return "";
    }
};

/**
 * @param {Object} args - search query string
 * @param {string} args.q - search query string
 * @returns {string} - compressed query string prefixed with a dot
 * @example
 * const query = "This is a very long search query that needs to be compressed for URL usage.";
 * const compressedQuery = compressRouteQuery({ q: query });
 * console.log(compressedQuery); // ".!~CoCwlgzgBJUIZQG4FMBOBPKAbA9gOwHMoJk5UBjEKARwFc1MAXEORqPZZAE2kZygBGyKORwBbAA6pkEElygAzHKigBVAEoAZKLQhwCyAHRA"
 */
const compressRouteQuery = ({ q }) => {
    if (q) return `${COMPRESSION_PREFIX}${compressQueryString(q)}`;

    return "";
};

/**
 * @param {Object} args - Arguments object
 * @param {string} args.q - search query string
 * @returns {string} - decompressed query string if it was compressed; otherwise returns the original query string
 * @example
 * const compressedQuery = ".!~CoCwlgzgBJUIZQG4FMBOBPKAbA9gOwHMoJk5UBjEKARwFc1MAXEORqPZZAE2kZygBGyKORwBbAA6pkEElygAzHKigBVAEoAZKLQhwCyAHRA";
 * const query = decompressRouteQuery({ q: compressedQuery });
 * console.log(query); // "This is a very long search query that needs to be compressed for URL usage."
 * @example
 * const query = "This is a normal search query.";
 * const decompressedQuery = decompressRouteQuery({ q: query });
 * console.log(decompressedQuery); // "This is a normal search query."
 */
const decompressRouteQuery = ({ q }) => {
    if (q && q.startsWith(COMPRESSION_PREFIX)) {
        return decompressQueryString(q.substring(COMPRESSION_INDEX));
    }
    return q;
}

/**
 * @param {Object} args - Arguments object
 * @param {string} args.query - search query string
 * @param {number} args.maxLength - maximum length of the returned string
 * @returns {string} - truncated query string for display purposes
 * @example
 * const query = "This is a very long search query that needs to be truncated for display purposes.";
 * const truncatedQuery = truncateQueryForDisplay({ query, maxLength: 30 });
 * console.log(truncatedQuery); // "This is a ver...lay purposes."
 * @example
 * const query = "Short query";
 * const truncatedQuery = truncateQueryForDisplay({ query, maxLength: 30 });
 * console.log(truncatedQuery); // "Short query"
 */
const truncateQueryForDisplay = ({
    query = "",
    maxLength = SEARCH_STRING_COMPRESSION_THRESHOLD
}) => {
    if (query.length <= maxLength) return query;
    // return half from start and half from end with ellipsis in middle
    const halfLength = Math.floor(maxLength / 2) - 2; // account for ellipsis
    return (
        query.slice(0, halfLength) +
        "..." +
        query.slice(query.length - halfLength)
    );
};


/**
 * @param {string} fileName - name of the file or link to the file
 * @returns {?string} - returns suffix of filename if the file name is a string and passes validation; otherwise returns undefined
 *
 * @example
 * const fileName = "test.docx";
 * const suffix = getFileNameSuffix(fileName);
 * console.log(suffix); // "docx"
 *
 * @example
 * const fileName = "test.msg";
 * const suffix = getFileNameSuffix(fileName);
 * console.log(suffix); // "Outlook"
 *
 * @example
 * const fileName = "https://www.google.com/test.html";
 * const suffix = getFileNameSuffix(fileName);
 * console.log(suffix); // ""
 */
const getFileNameSuffix = (fileName) => {
    // early return if fileName is not a string or is otherwise invalid
    if (
        typeof fileName !== "string"
            || !fileName.includes(".")
            || lodashEndsWith(fileName, ".")
    ) {
        return undefined;
    }

    let fileNameString;

    // if fileName is a URL, leverage URL interface to get cleaned pathname
    try {
        let url = new URL(fileName);
        fileNameString = url.pathname.toLowerCase();
    } catch (_error) {
        // if fileName is not a URL, use it as is
        fileNameString = fileName.toLowerCase();
    }

    const pathArray = fileNameString.split(".");

    if (pathArray.length < 2) return undefined;

    const suffix = pathArray.pop();

    if (
        suffix.length > 4
            || suffix.length < 2
            || INVALID_SUFFIXES.includes(suffix) // html, htm
    ) {
        return undefined;
    }

    return SUFFIX_DICT[suffix] ?? suffix.toUpperCase();
};

/**
 * @param {Object} args - Arguments object
 * @param {string} args.fileName - The name of the file
 * @param {string} args.uid - The uid of the document
 *
 * @returns {string} - HTML string for the file type button
 */
const getFileTypeButton = ({ fileName, uid }) => {
    const fileTypeSuffix = getFileNameSuffix(fileName);

    let fileTypeButton;
    if (fileName && fileTypeSuffix) {
        fileTypeButton = `<span data-testid='download-chip-${uid}' class='result__link--file-type'>${fileTypeSuffix}</span>`;
    }

    return `${fileTypeButton ?? ""}`;
};

/**
 * @param {string} link - URL to extract domain from
 * @returns {string} - domain of the link without "www." prefix
 * @example
 * const link = "https://www.example.com/path/to/resource";
 * const domain = getLinkDomain(link);
 * console.log(domain); // "example.com"
 * @example
 * const link = "not a valid url";
 * const domain = getLinkDomain(link);
 * console.log(domain); // ""
 **/
const getLinkDomain = (link) => {
    try {
        const url = new URL(link);
        return url.hostname.replace(/^www\./, "");
    } catch (_error) {
        return "";
    }
};

/**
 * @param {Object} args - Arguments object
 * @param {string} args.url - URL from which to extract domain
 * @param {string} args.className - CSS class to apply to the domain string span
 * @return {string} - HTML string with the domain wrapped in a span with the provided class name
 * @example
 * const args = {
 *       url: "https://www.example.com/path/to/resource",
 *       className: "domain-class"
 *   };
 *   const domainString = getLinkDomainString(args);
 *   console.log(domainString); // "<span class='domain-class'>example.com</span>"
 * @example
 *   const args = {
 *       url: "not a valid url",
 *       className: "domain-class"
 *   };
 *   const domainString = getLinkDomainString(args);
 *   console.log(domainString); // ""
 */
const getLinkDomainString = ({ url, className }) => {
    const domain = getLinkDomain(url);

    if (isEmpty(domain)) {
        return "";
    }

    return `<span class='${className}'>${domain}</span>`;
};

/**
 * @param {string} linkTitle - Title of the link
 * @param {string} domainString - Domain string to append to the link title
 * @param {string} fileTypeButton - HTML string for the file type button
 * @return {string} - HTML string with the link title, domain string, and file type button
 * @example
 * const linkTitle = "Example Link";
 * const domainString = "<span class='domain-class'>example.com</span>";
 * const fileTypeButton = "<span class='result__link--file-type'>PDF</span>";
 * const linkDomainFileTypeEl = getLinkDomainFileTypeEl(linkTitle, domainString, fileTypeButton);
 * console.log(linkDomainFileTypeEl); // "Example Link<span class='result__link--file-type'>PDF</span><span class='domain-class'>example.com</span>"
 */
const getLinkDomainFileTypeEl = (linkTitle, domainString, fileTypeButton) => {
    const fileString = fileTypeButton
        ? `${fileTypeButton}${domainString && "<span class='spacer__span'> </span>"}`
        : "";
    const domainFileTypeEl = domainString
        ? `${fileString}${domainString}`
        : `${fileString}`;

    return `<span class='result__label--title'>${linkTitle}</span><span class='spacer__span'> </span>${domainFileTypeEl}`;
};


/*
 * @param {Object} query - $route.query object from Vue Router
 * @returns {string} - query string in `${key}=${value}&${key}=${value}` format
 */
const getRequestParams = ({ queryParams, disallowList = [] }) => {
    const rawParams = Object.entries(queryParams).filter(
        ([key, _value]) => PARAM_VALIDATION_DICT[key]
    );

    // if no type, set type to all so we can handle disallowList
    if (rawParams.filter(([key, _value]) => key === "type").length === 0) {
        rawParams.push(["type", "all"]);
    }

    const formattedParams = rawParams
        .map(([key, value]) => {
            const valueArray = Array.isArray(value) ? value : [value];
            const filteredValues = valueArray.filter((value) =>
                PARAM_VALIDATION_DICT[key](value)
            );

            return filteredValues
                .map((v) => {
                    if (key === "type") {
                        // if type='all', early return with explicit query params
                        if (v === "all") {
                            if (disallowList.length === 0) return "";

                            return disallowList
                                .filter((type) =>
                                    PARAM_VALIDATION_DICT["type"](type)
                                )
                                .map((type) => {
                                    const typeArg =
                                        type === "external" ? "public" : type;
                                    return `show_${typeArg}=false`;
                                })
                                .join("&");
                        }

                        // Since the API defaults to showing all types, we need to
                        // pass display_<type>=false for the types that are not in the array
                        // of types that the user wants to see.
                        const typeArray = v.split(",");

                        const differenceArray = lodashDifference(
                            DOCUMENT_TYPES,
                            typeArray
                        );

                        const unionWithDisallowed = [
                            ...new Set([...differenceArray, ...disallowList]),
                        ];

                        const paramsArray = unionWithDisallowed.map((type) => {
                            const typeArg =
                                type === "external" ? "public" : type;
                            return `show_${typeArg}=false`;
                        });

                        return paramsArray.join("&");
                    } else {
                        return `${PARAM_MAP[key]}=${
                            key in PARAM_ENCODE_DICT
                                ? PARAM_ENCODE_DICT[key](v)
                                : v
                        }`;
                    }
                })
                .join("&");
        })
        .filter(([_key, value]) => !isEmpty(value))
        .join("&");

    return formattedParams;
};

const parseError = (err) => {
    console.info(err);
    const errMessage = err.errors
        ? err.errors[Object.keys(err.errors)[0]][0]
        : err.message;

    const message = errMessage;
    try {
        const code = Object.keys(err.errors)[0];
        const status = lodashGet(err, "status");
        const requestId = lodashGet(err, "requestId");
        const error = new Error(message);
        error.code = code;
        error.requestId = requestId;
        error.root = err;
        error.status = status;
        return error;
    } catch {
        if (err.detail) {
            return err;
        }
        return new Error(message);
    }
};

// a promise friendly delay function
const delay = (seconds) => {
    return new Promise((resolve) => {
        lodashDelay(resolve, seconds * 1000);
    });
};

/**
 * Converts date from YYYY-MM-DD to MMM DD, YYYY
 *
 * @param {string} kebabDate - date in `YYYY-MM-DD` format
 * @returns {string} - date in `MMM DD, YYYY` format
 */
const niceDate = (kebabDate) => {
    if (isNil(kebabDate)) return "N/A";
    if (isString(kebabDate) && isEmpty(kebabDate)) return "N/A";
    const date = new Date(`${kebabDate}T12:00:00.000-05:00`);
    const month = date.toLocaleString("default", { month: "short" });
    const day = date.getDate();
    const year = date.getFullYear();
    return `${month} ${day}, ${year}`;
};

const getQueryParam = (location, key) => {
    const queryParams = new URL(location).searchParams;
    return queryParams.get(key);
};

/**
 *
 * @param length {number} - number of elements in array
 * @returns {Array<number>} - array containing sequential numbers beginning with 1
 */
const createOneIndexedArray = (length) => {
    return Array.from({ length }, (_, i) => i + 1);
};

/**
 * @param string {string} - string with surrounding quotes
 * @returns {string} - string with surrounding quotes removed
 */
const stripQuotes = (string) => {
    if (!string || typeof string !== "string") {
        return string;
    }
    return string.replace(/^['"]|['"]$/g, "");
};

/**
 * @param htmlString {string} - string of HTML markup
 * @param tagClass {string} - class to identify target HTML tag
 * @returns {Array<string>} - array of of highlight terms as strings
 */
const getTagContent = (htmlString, tagClass) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, "text/html");
    const highlightCollection = doc.getElementsByClassName(tagClass);
    const highlightTermsArray = [...highlightCollection].map((highlightEl) => {
        return highlightEl.innerHTML;
    });
    return highlightTermsArray;
};

const createRegResultLink = (
    { headline, title, part_number, section_number, date, section_title },
    baseUrl,
    query
) => {
    // get highlight content from headline
    const highlightedTermsArray = getTagContent(headline, "search-highlight");
    const rawQuery = query.replaceAll("%", "%25");
    const uniqTermsArray = Array.from(
        new Set([rawQuery, ...highlightedTermsArray])
    );

    const highlightParams =
        uniqTermsArray.length > 0 ? `?q=${uniqTermsArray.join(",")}` : "";

    let section = section_number;
    let location = `${part_number}-${section_number}`;

    if (section_title.includes("Appendix")) {
        section = `Subpart-${section}`;
        location = `${section_title.split("-")[0].trim().replace(/\s/g, "-")}`;
    }

    return `${baseUrl}${title}/${part_number}/${section}/${date}/${highlightParams}#${location}`;
};

/**
 * @param count {number} - total number of results
 * @param page {number} - current page number
 * @param pageSize {number} - number of results per page
 * @returns  {Array<number>} - an array containing two entries: firstInRange at index 0 and lastInRange at index 1
 */
const getCurrentPageResultsRange = ({ count, page = 1, pageSize }) => {
    const maxInRange = page * pageSize;
    const minInRange = maxInRange - pageSize;

    const firstInRange = minInRange + 1;
    const lastInRange =
        maxInRange > count ? (count % pageSize) + minInRange : maxInRange;

    return [firstInRange, lastInRange];
};

/**
 * @param {Object} args - Arguments object
 * @param {number} args.resources - array of resource objects
 * @param {number} args.categories - array of category objects
 * @param {string} args.apiUrl - version of API passed in from Django.  Ex: `/v2/` or `/v3/`
 */
const formatResourceCategories = ({
    resources = [],
    categories = [],
    apiUrl,
}) => {
    const categoriesClone = [...categories];

    resources.forEach((resource) => {
        if (resource.type === "internal_file") {
            resource.url = `${apiUrl}resources/internal/files/${resource.uid}`;
        }

        if (
            resource.category?.type === "public_category" ||
            resource.category?.type === "internal_category"
        ) {
            const existingCategory = categoriesClone.find(
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
                newCategory.subcategories = [];
                categoriesClone.push(newCategory);
            }
        }
    });

    resources.forEach((resource) => {
        if (
            resource.category?.type === "public_subcategory" ||
            resource.category?.type === "internal_subcategory"
        ) {
            categoriesClone.forEach((category) => {
                if (!category.subcategories) {
                    return;
                }

                category.subcategories.forEach((subcategory) => {
                    if (subcategory.name === resource.category.name) {
                        if (!subcategory.supplemental_content) {
                            subcategory.supplemental_content = [];
                        }
                        subcategory.supplemental_content.push(resource);
                    }
                });
            });
        }
    });

    const returnArr = categoriesClone
        .filter((category) => {
            if (category.supplemental_content || category.show_if_empty)
                return true;

            const hasPopulatedSubcategory =
                category.subcategories &&
                category.subcategories.some(
                    (subcategory) => subcategory.supplemental_content
                );

            if (hasPopulatedSubcategory) return true;

            return false;
        })
        .sort((a, b) => a.order - b.order);

    returnArr.forEach((category) => {
        category.subcategories.sort((a, b) => a.order - b.order);
    });

    return returnArr;
};

const formatDate = (value) => {
    if (!value) {
        return "Invalid Date";
    }

    const date = new Date(value);

    if (date.toString() === "Invalid Date") {
        return date.toString();
    }

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

/**
 * Recursively search through DOM Element and its children and
 * surround strings that match `highlightString` with <mark> tags
 *
 * @param {HTMLElement} element - element to mutate
 * @param {string} highlightString - string to match
 */
function addMarks(element, highlightString) {
    function escapeRegex(string) {
        return string.replace(/[/\-\\^$*+?.()|[\]{}]/g, "\\$&");
    }

    const regex = new RegExp(escapeRegex(highlightString));

    if (element.nodeType === document.TEXT_NODE) {
        // note `nodeValue` vs `innerHTML`
        // nodeValue gives inner text without Vue component markup tags;
        // innerHTML gives text with Vue Component markup tags;
        // Currently there is only the tooltip <trigger-btn> tag at beginning
        const text = element.nodeValue;
        if (text.toUpperCase().indexOf(highlightString.toUpperCase()) !== -1) {
            // ignore citation node at bottom of section
            if (element?.parentNode?.className === "citation-node") {
                return;
            }

            if (element?.parentNode?.nodeName === "A") {
                const closestParagraph = element.parentNode.closest("p");
                if (closestParagraph?.className === "citation-node") {
                    return;
                }
            }

            const innerHtmlOfParentNode = element.parentNode.innerHTML;
            const indexOfText = innerHtmlOfParentNode.indexOf(text);
            const textToKeep = innerHtmlOfParentNode.slice(0, indexOfText);
            const textToAlter = innerHtmlOfParentNode.slice(indexOfText);
            const newText = textToAlter.replace(
                regex,
                "<mark class='highlight'>$&</mark>"
            );
            element.parentNode.innerHTML = textToKeep + newText;
            return;
        }
    } else if (element.nodeType === document.ELEMENT_NODE) {
        for (let i = 0; i < element.childNodes.length; i++) {
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
                if (text.length > 1) {
                    addMarks(targetedSection, text);
                }
            });
        }
    }
};

/**
 * Scroll to top of HTML element while taking
 * heights of other elements into consideration
 *
 * @param {HTMLElement} element - scroll to this element
 * @param {number} [offsetPx=0] - pixels to offset scroll from top of screen
 */
const scrollToElement = (element, offsetPx = 0) => {
    const position = element.getBoundingClientRect();
    window.scrollTo(position.x, element.offsetTop - offsetPx);
};

/**
 * @param {string} act - full name of act. Ex: "Social Security Act"
 * @param {Array<{[key: string]: string}>} actTypes - array of objects with act type abbreviations as keys and act type names as values
 *
 * @returns {string} - act type abbreviation. Ex: "ssa"
 */
const getActAbbr = ({ act, actTypes }) =>
    Object.keys(
        actTypes.find((actTypeObj) => Object.values(actTypeObj).includes(act))
    )[0];

/**
 * @param {Array<{act: string, title: number, title_roman: string}>} actsResults - array of title objects
 * @param {Array<{[key: string]: string}>} actTypes - array of objects with act type abbreviations as keys and act type names as values
 *
 * @returns {Object<{[key: string]: Object<{name: string, titles: Array<{title: string, titleRoman: string}>}>}>} - object with act type abbreviations as keys and objects with act type names and titles as values
 */
const shapeTitlesResponse = ({ actsResults, actTypes }) => {
    const returnObj = {};

    // reshape acts response to what we need
    actsResults.forEach((title) => {
        const actAbbr = getActAbbr({ act: title.act, actTypes });
        if (!returnObj[actAbbr]) {
            returnObj[actAbbr] = {
                name: title.act,
                titles: [],
            };
        }

        returnObj[actAbbr].titles.push({
            title: title.title.toString(),
            titleRoman: title.title_roman,
        });
    });

    return returnObj;
};

/**
 * @param {Array.<Array<{id: string, name: string, date: string, last_updated: string, depth: number}>>} resultsArr - array of arrays of title objects
 *
 * @returns {Object.<string, string>} - Object with Part numbers as keys and YYYY-MM-DD datestring as values
 */
const createLastUpdatedDates = (resultsArr) => {
    const combinedResults = resultsArr.flat(1).reduce(
        (accumulator, current) => ({
            ...accumulator,
            [current.name]: current,
        }),
        {}
    );

    return Object.fromEntries(
        Object.entries(combinedResults).map((arr) => [arr[1].name, arr[1].date])
    );
};

const getCurrentSectionFromHash = (windowHash) => {
    const hash = windowHash.substring(1);
    const citations = hash.split("-");
    return citations.slice(0, 2).join("-");
};

/**
 * @param {Array<object>} sectionList - array of Table of Contents objects from getChildTOC
 * @returns {Array<string>} - array of section identifier numbers as strings
 */
const getSectionsRecursive = (tocPartsList) => {
    if (!tocPartsList || !Array.isArray(tocPartsList)) {
        return [];
    }
    return tocPartsList.flatMap((tocPart) => {
        if (tocPart.type !== "section")
            return getSectionsRecursive(tocPart.children);
        return tocPart.identifier[1];
    });
};

const getFieldVal = ({ item, fieldName }) => {
    if (item?.resource) {
        // content-search
        return item.resource[fieldName];
    } else if (item?.reg_text) {
        return item.reg_text[fieldName];
    } else {
        return item?.[fieldName];
    }
};

const getFrDocType = (doc) => {
    if (doc?.withdrawal) {
        return "WD";
    }
    if (doc?.correction) {
        return "CORR";
    }
    return doc?.action_type || doc?.category?.name || doc?.type;
};

const deserializeResult = (obj) => {
    const returnObj = {};

    returnObj.action_type = getFieldVal({
        item: obj,
        fieldName: "action_type",
    });
    returnObj.category = getFieldVal({ item: obj, fieldName: "category" });
    returnObj.cfr_citations = getFieldVal({
        item: obj,
        fieldName: "cfr_citations",
    });
    returnObj.usc_citations = getFieldVal({
        item: obj,
        fieldName: "usc_citations",
    });
    returnObj.act_citations = getFieldVal({
        item: obj,
        fieldName: "act_citations",
    });
    returnObj.content_headline = obj.content_headline;
    returnObj.correction = getFieldVal({ item: obj, fieldName: "correction" });
    returnObj.date = getFieldVal({ item: obj, fieldName: "date" });
    returnObj.document_id = getFieldVal({
        item: obj,
        fieldName: "document_id",
    });
    returnObj.file_name = getFieldVal({ item: obj, fieldName: "file_name" });
    returnObj.id = getFieldVal({ item: obj, fieldName: "id" });
    returnObj.name_headline = obj.name_headline;
    returnObj.node_id = obj.reg_text?.node_id;
    returnObj.node_type = obj.reg_text?.node_type;
    returnObj.part_number = obj.reg_text?.part_number;
    returnObj.part_title = obj.reg_text?.part_title;
    returnObj.subpart_title = obj.reg_text?.subpart_title;
    returnObj.reg_title = obj.reg_text?.title;
    returnObj.subjects = getFieldVal({ item: obj, fieldName: "subjects" });
    returnObj.summary = obj.summary;
    returnObj.summary_headline = obj.summary_headline;
    returnObj.summary_string = obj.summary_string;
    returnObj.title = obj.reg_text
        ? getFieldVal({ item: obj, fieldName: "node_title" })
        : getFieldVal({ item: obj, fieldName: "title" });
    returnObj.type =
        getFieldVal({ item: obj, fieldName: "type" }) ?? "reg_text";
    returnObj.uid = getFieldVal({ item: obj, fieldName: "uid" });
    returnObj.url = getFieldVal({ item: obj, fieldName: "url" });
    returnObj.withdrawal = getFieldVal({ item: obj, fieldName: "withdrawal" });

    return returnObj;
};

const hasRegulationCitations = ({ doc, partsLastUpdated }) => {
    const regCitations = doc.cfr_citations
        ? doc.cfr_citations.filter((location) => {
            const { part } = location;
            return partsLastUpdated[part];
        })
        : [];

    return regCitations.length > 0;
};

/**
 * Checks if the document has statute citations.
 *
 * @param {Object} doc - The document object.
 * @param {Array} doc.act_citations - Array of act citations.
 * @param {Array} doc.usc_citations - Array of USC citations.
 * @returns {boolean} - Returns true if the document has both statute citation fields in the response and if one of those fields has a length > 0, false otherwise.
 */
const hasStatuteCitations = ({ doc }) => {
    // ensure that both act_citations and usc_citations fields are present
    if (!doc.act_citations || !doc.usc_citations) return false;

    // if both fields exist, check if either field has citations
    return doc.act_citations.length > 0 || doc.usc_citations.length > 0;
};

export {
    addMarks,
    compressQueryString,
    compressRouteQuery,
    createLastUpdatedDates,
    createRegResultLink,
    COMPRESSION_PREFIX,
    COUNT_TYPES_MAP,
    createOneIndexedArray,
    decompressQueryString,
    decompressRouteQuery,
    delay,
    deserializeResult,
    DOCUMENT_TYPES,
    DOCUMENT_TYPES_MAP,
    EventCodes,
    formatDate,
    formatResourceCategories,
    getActAbbr,
    getCurrentPageResultsRange,
    getCurrentSectionFromHash,
    getFieldVal,
    getFileNameSuffix,
    getFileTypeButton,
    getFrDocType,
    getLinkDomain,
    getLinkDomainFileTypeEl,
    getLinkDomainString,
    getQueryParam,
    getRequestParams,
    getSectionsRecursive,
    getTagContent,
    hasRegulationCitations,
    hasStatuteCitations,
    highlightText,
    MAX_QUERY_LENGTH,
    niceDate,
    PARAM_ENCODE_DICT,
    PARAM_VALIDATION_DICT,
    parseError,
    SEARCH_STRING_COMPRESSION_THRESHOLD,
    SEARCH_STRING_TRUNCATE_THRESHOLD,
    scrollToElement,
    shapeTitlesResponse,
    stripQuotes,
    truncateQueryForDisplay,
};
