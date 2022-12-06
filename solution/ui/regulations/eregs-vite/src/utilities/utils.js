/* eslint-disable */
import _delay from "lodash/delay";
import _endsWith from "lodash/endsWith";
import _filter from "lodash/filter";
import _forEach from "lodash/forEach";
import _get from "lodash/get";
import _indexOf from "lodash/indexOf";
import _isArray from "lodash/isArray";
import _isBoolean from "lodash/isBoolean";
import _isEmpty from "lodash/isEmpty";
import _isFunction from "lodash/isFunction";
import _isNil from "lodash/isNil";
import _isNumber from "lodash/isNumber";
import _isObject from "lodash/isObject";
import _isString from "lodash/isString";
import _keys from "lodash/keys";
import _map from "lodash/map";
import _random from "lodash/random";
import _set from "lodash/set";
import _transform from "lodash/transform";

//import numeral from "numeral";

/**
 * Converts the given Map object to an array of values from the map
 */
function mapToArray(map) {
    const result = [];
    // converting map to result array
    map.forEach((value) => result.push(value));
    return result;
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

function swallowError(promise, fn = () => ({})) {
    try {
        return Promise.resolve()
            .then(() => promise)
            .catch((err) => fn(err));
    } catch (err) {
        return fn(err);
    }
}

// a promise friendly delay function
function delay(seconds) {
    return new Promise((resolve) => {
        _delay(resolve, seconds * 1000);
    });
}

// function niceNumber(value) {
//     if (_isNil(value)) return "N/A";
//     if (_isString(value) && _isEmpty(value)) return "N/A";
//     return numeral(value).format("0,0");
// }

// function nicePrice(value) {
//     if (_isNil(value)) return "N/A";
//     if (_isString(value) && _isEmpty(value)) return "N/A";
//     return numeral(value).format("0,0.00");
// }

// YYYY-MM-DD to MMM DD, YYYY
const niceDate = (kebabDate) => {
    if (_isNil(kebabDate)) return "N/A";
    if (_isString(kebabDate) && _isEmpty(kebabDate)) return "N/A";
    const date = new Date(`${kebabDate}T12:00:00.000-05:00`);
    const month = date.toLocaleString("default", { month: "short" });
    const day = date.getDate();
    const year = date.getFullYear();
    return `${month} ${day}, ${year}`;
};

function getQueryParam(location, key) {
    const queryParams = new URL(location).searchParams;
    return queryParams.get(key);
}

function addQueryParams(location, params) {
    const url = new URL(location);
    const queryParams = url.searchParams;

    const keys = _keys(params);
    keys.forEach((key) => {
        queryParams.append(key, params[key]);
    });

    const newUrl = url.origin + url.pathname;

    if (queryParams.toString()) {
        newUrl += `?${queryParams.toString()}`;
    }

    newUrl += url.hash;
    return newUrl;
}

function removeQueryParams(location, keys) {
    const url = new URL(location);
    const queryParams = url.searchParams;

    keys.forEach((key) => {
        queryParams.delete(key);
    });

    const newUrl = url.origin + url.pathname;

    if (queryParams.toString()) {
        newUrl += `?${queryParams.toString()}`;
    }

    newUrl += url.hash;
    return newUrl;
}

function getCategoryTree(categories) {
    let catOptions = [];
    let categoryDict = {};
    for (let category in categories) {
        let cat = categories[category];
        if (cat.object_type === "subcategory") {
            if (cat.parent.name in categoryDict) {
                categoryDict[cat.parent.name].children.push({
                    id: cat.name,
                    label: cat.name,
                });
            } else {
                categoryDict[cat.parent.name] = {
                    id: cat.parent.name,
                    label: cat.parent.name,
                    children: [{ id: cat.name, label: cat.name }],
                };
            }
        } else if (!(cat.name in categoryDict)) {
            categoryDict[cat.name] = {
                id: cat.name,
                label: cat.name,
                children: [],
            };
        }
    }

    for (let category in categoryDict) {
        if (categoryDict[category].children.length === 0) {
            delete categoryDict[category].children;
        }
        catOptions.push(categoryDict[category]);
    }

    return catOptions;
}

function getFragmentParam(location, key) {
    const fragmentParams = new URL(location).hash;
    const hashKeyValues = {};
    const params = fragmentParams.substring(1).split("&");
    if (params) {
        params.forEach((param) => {
            const keyValueArr = param.split("=");
            const currentKey = keyValueArr[0];
            const value = keyValueArr[1];
            if (value) {
                hashKeyValues[currentKey] = value;
            }
        });
    }
    return hashKeyValues[key];
}

function removeFragmentParams(location, keyNamesToRemove) {
    const url = new URL(location);
    const fragmentParams = url.hash;
    const hashStr = "#";
    const params = fragmentParams.substring(1).split("&");
    if (params) {
        params.forEach((param) => {
            const keyValueArr = param.split("=");
            const currentKey = keyValueArr[0];
            const value = keyValueArr[1];
            // Do not include the currentKey if it is the one specified in the array of keyNamesToRemove
            if (value && _indexOf(keyNamesToRemove, currentKey) < 0) {
                hashStr = `${currentKey}${currentKey}=${value}`;
            }
        });
    }
    return `${url.protocol}//${url.host}${url.search}${
        hashStr === "#" ? "" : hashStr
    }`;
}

function isAbsoluteUrl(url) {
    return /^https?:/.test(url);
}

function removeNulls(obj = {}) {
    Object.keys(obj).forEach((key) => {
        if (obj[key] === null) delete obj[key];
    });

    return obj;
}

// remove the "end" string from "str" if it exists
function chopRight(str = "", end = "") {
    if (!_endsWith(str, end)) return str;
    return str.substring(0, str.length - end.length);
}

const isFloat = (n) => {
    return n % 1 !== 0;
};

// input [ { <name>: { label, desc, ..} }, { <name2>: { label, desc } } ]
// output { <name>: { label, desc, ..}, <name2>: { label, desc } }
function childrenArrayToMap(arr) {
    const result = {};
    arr.forEach((item) => {
        const key = _keys(item)[0];
        result[key] = item[key];
    });
    return result;
}

const idGeneratorCount = 0;

function generateId(prefix = "") {
    idGeneratorCount += 1;
    return `${prefix}_${idGeneratorCount}_${Date.now()}_${_random(0, 1000)}`;
}

// Given a Map and an array of items (each item MUST have an "id" prop), consolidate
// the array in the following manner:
// - if an existing item in the map is no longer in the array of items, remove the item from the map
// - if an item in the array is not in the map, then add it to the map using the its "id" prop
// - if an item in the array is also in the map, then call 'mergeExistingFn' with the existing item
//   and the new item. It is expected that this 'mergeExistingFn', will know how to merge the
//   properties of the new item into the existing item.
function consolidateToMap(map, itemsArray, mergeExistingFn) {
    const unprocessedKeys = {};

    map.forEach((_value, key) => {
        unprocessedKeys[key] = true;
    });

    itemsArray.forEach((item) => {
        const { id } = item;
        const hasExisting = map.has(id);
        const exiting = map.get(id);

        if (!exiting) {
            map.set(item.id, item);
        } else {
            mergeExistingFn(exiting, item);
        }

        if (hasExisting) {
            delete unprocessedKeys[id];
        }
    });

    _forEach(unprocessedKeys, (_value, key) => {
        map.delete(key);
    });
}

/**
 * Converts an object graph into flat object with key/value pairs.
 * The rules of object graph to flat key value transformation are as follows.
 * 1. An already flat attribute with primitive will not be transformed.
 *    For example,
 *      input = { someKey: 'someValue' } => output = { someKey: 'someValue' }
 * 2. A nested object attribute will be flattened by adding full attribute path '<attributeName>.' (the paths are as per lodash's get and set functions)
 *    For example,
 *      input = { someKey: { someNestedKey: 'someValue' } } => output = { 'someKey.someNestedKey': 'someValue' }
 * 3. An array attribute will be flattened by adding correct path '<attributeName>[<elementIndex>]' prefix. (the paths are as per lodash's get and set functions)
 *    For example,
 *      input = { someKey: [ 'someValue1', 'someValue2' ] } => output = { 'someKey[0]': 'someValue1', 'someKey[1]': 'someValue2' }
 *      input = { someKey: [ 'someValue1', ['someValue2','someValue3'], 'someValue4' ] } => output = { 'someKey[0]': 'someValue1', 'someKey[1][0]': 'someValue2', 'someKey[1][1]': 'someValue3', 'someKey[2]': 'someValue4' }
 *      input = { someKey: [{ someNestedKey: 'someValue' }] } => output = { 'someKey[0].someNestedKey': 'someValue' }
 *
 * @param obj An object to flatten
 * @param filterFn An optional filter function that allows filtering out certain attributes from being included in the flattened result object. The filterFn is called with 3 arguments (result, value, key) and is expected to return true to include
 *   the key in the result or false to exclude the key from the result.
 * @param keyPrefix A optional key prefix to include in all keys in the resultant flattened object.
 * @param accum An optional accumulator to use when performing the transformation
 * @returns {*}
 */
function flattenObject(obj, filterFn = () => true, keyPrefix = "", accum = {}) {
    function toFlattenedKey(key, idx) {
        let flattenedKey;
        if (_isNil(idx)) {
            if (_isNumber(key)) {
                flattenedKey = keyPrefix ? `${keyPrefix}[${key}]` : `[${key}]`;
            } else {
                flattenedKey = keyPrefix ? `${keyPrefix}.${key}` : key;
            }
        } else {
            flattenedKey = keyPrefix
                ? `${keyPrefix}.${key}[${idx}]`
                : `${key}[${idx}]`;
        }
        return flattenedKey;
    }

    return _transform(
        obj,
        (result, value, key) => {
            if (filterFn(result, value, key)) {
                if (_isArray(value)) {
                    const idx = 0;
                    _forEach(value, (element) => {
                        const flattenedKey = toFlattenedKey(key, idx);
                        if (_isObject(element)) {
                            flattenObject(
                                element,
                                filterFn,
                                flattenedKey,
                                result
                            );
                        } else {
                            result[flattenedKey] = element;
                        }
                        ++idx;
                    });
                } else {
                    const flattenedKey = toFlattenedKey(key);
                    if (_isObject(value)) {
                        flattenObject(value, filterFn, flattenedKey, result);
                    } else {
                        result[flattenedKey] = value;
                    }
                }
            }
            return result;
        },
        accum
    );
}

/**
 * Converts an object with key/value pairs into object graph. This function is inverse of flattenObject.
 * i.e., unFlattenObject(flattenObject(obj)) = obj
 *
 * The rules of key/value pairs to object graph transformation are as follows.
 * 1. Key that does not contain delimiter will not be transformed.
 *    For example,
 *      input = { someKey: 'someValue' } => output = { someKey: 'someValue' }
 * 2. Key/Value containing delimiter will be transformed into object path
 *    For example,
 *      input = { someKey_someNestedKey: 'someValue' } => output = { someKey: { someNestedKey: 'someValue' } }
 * 3. Key/Value containing delimiter and integer index will be transformed into object containing array.
 *    For example,
 *      input = { someKey_0: 'someValue1', someKey_1: 'someValue2' } => output = { someKey: [ 'someValue1', 'someValue2' ] }
 *      input = { "someKey_0": "someValue1", "someKey_1_0": "someValue2", "someKey_1_1": "someValue3", "someKey_2": "someValue4" } => output = { someKey: [ 'someValue1', ['someValue2','someValue3'], 'someValue4' ] }
 *      input = { someKey_0_someNestedKey: 'someValue' } => output = { someKey: [{ someNestedKey: 'someValue' }] }
 *
 * @param obj An object to flatten
 * @param filterFn An optional filter function that allows filtering out certain attributes from being included in the flattened result object. The filterFn is called with 3 arguments (result, value, key) and is expected to return true to include
 *   the key in the result or false to exclude the key from the result.
 * @param keyPrefix A optional key prefix to include in all keys in the resultant flattened object.
 * @returns {*}
 */
function unFlattenObject(keyValuePairs, filterFn = () => true) {
    return _transform(
        keyValuePairs,
        (result, value, key) => {
            if (filterFn(result, value, key)) {
                _set(result, key, value);
            }
            return result;
        },
        {}
    );
}

function isAmountFormatCorrect(no) {
    const noStr = `${no}`;
    return /^\d{0,7}([.]{0,1}\d{0,2})$/.test(noStr);
}

function formatAmount(amount) {
    return amount
        .toFixed(2)
        .toString()
        .replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,");
}

// convert current date to YYYY-MM-DD
const getKebabDate = (date = new Date()) => {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate();

    return `${year}-${month}-${day}`;
};

const getKebabLabel = (label) => {
    if (!label) return "na-label";
    return `${label.join("-")}`;
};

const getKebabTitle = (label) => {
    return `${getKebabLabel(label)}-title`;
};

const getDisplayName = (label, title = 42) => {
    if (!label) return "na-label";
    return `${title} ${label.join(".")}`;
};

// lifted straight from django pdepth templatetag
const getParagraphDepth = (value) => {
    const sectionDepth = 2;

    const labelLength = value?.label?.length;
    const markerLength = value?.marker?.length;

    let depth = labelLength - sectionDepth;

    if (markerLength > 1) {
        depth = depth - (markerLength - 1);
    }

    if (depth < 1) return 1;

    return depth;
};

function capitalizeFirstLetter(string) {
    return string[0].toUpperCase() + string.slice(1);
}

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
    return string.replace(/(^")|("$)/g, "");
};

/**
 * @param htmlString {string} - string of HTML markup
 * @param tagClass {string} - class to identify target HTML tag
 * @returns {string} - comma-separated string of unique highlight terms
 */
const getTagContent = (htmlString, tagClass) => {
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlString, "text/html");
    const highlightCollection = doc.getElementsByClassName(tagClass);
    const highlightTermsArray = [...highlightCollection].map((highlightEl) => {
        return highlightEl.innerHTML;
    });
    const uniqTermsArray = Array.from(new Set(highlightTermsArray));
    return uniqTermsArray.join(",");
};

export {
    mapToArray,
    parseError,
    swallowError,
    delay,
    //niceNumber,
    getQueryParam,
    removeQueryParams,
    addQueryParams,
    getFragmentParam,
    removeFragmentParams,
    //nicePrice,
    isFloat,
    removeNulls,
    chopRight,
    childrenArrayToMap,
    isAbsoluteUrl,
    generateId,
    consolidateToMap,
    flattenObject,
    unFlattenObject,
    isAmountFormatCorrect,
    formatAmount,
    niceDate,
    getKebabDate,
    getKebabLabel,
    getKebabTitle,
    getParagraphDepth,
    getDisplayName,
    getCategoryTree,
    capitalizeFirstLetter,
    createOneIndexedArray,
    stripQuotes,
    getTagContent,
};
