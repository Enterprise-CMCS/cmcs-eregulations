//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//

var script$5 = {
    name: "related-rule",

    props: {
        title: {
            type: String,
            required: true,
        },
        type: {
            type: String,
            required: true,
        },
        citation: {
            type: String,
            required: true,
        },
        publication_date: String,
        document_number: {
            type: String,
            required: true,
        },
        html_url: {
            type: String,
            required: true,
        },
        action: {
            type: String,
            required: true,
        },
    },

    computed: {
        expandedType: function () {
            if (this.type === "Rule") {
                return "Final";
            } else if(this.type === "Proposed Rule" && this.action === "Proposed rule."){
              return "NPRM"
            } else if(this.type === "Proposed Rule" && this.action === "Request for information."){
              return "RFI"
            }
            return "Unknown";
        },
        getClassList: function(){
          return this.expandedType === "Final" ? "recent-flag indicator" : "recent-flag indicator secondary-indicator"
        }
    },

    methods: {},
    filters: {
        formatDate: function (value) {
            const date = new Date(value);
            const options = {
                year: "numeric",
                month: "long",
                day: "numeric",
                timeZone: "UTC",
            };
            const format = new Intl.DateTimeFormat("en-US", options);
            return format.format(date);
        },
    },
};

function normalizeComponent(template, style, script, scopeId, isFunctionalTemplate, moduleIdentifier /* server only */, shadowMode, createInjector, createInjectorSSR, createInjectorShadow) {
    if (typeof shadowMode !== 'boolean') {
        createInjectorSSR = createInjector;
        createInjector = shadowMode;
        shadowMode = false;
    }
    // Vue.extend constructor export interop.
    const options = typeof script === 'function' ? script.options : script;
    // render functions
    if (template && template.render) {
        options.render = template.render;
        options.staticRenderFns = template.staticRenderFns;
        options._compiled = true;
        // functional template
        if (isFunctionalTemplate) {
            options.functional = true;
        }
    }
    // scopedId
    if (scopeId) {
        options._scopeId = scopeId;
    }
    let hook;
    if (moduleIdentifier) {
        // server build
        hook = function (context) {
            // 2.3 injection
            context =
                context || // cached call
                    (this.$vnode && this.$vnode.ssrContext) || // stateful
                    (this.parent && this.parent.$vnode && this.parent.$vnode.ssrContext); // functional
            // 2.2 with runInNewContext: true
            if (!context && typeof __VUE_SSR_CONTEXT__ !== 'undefined') {
                context = __VUE_SSR_CONTEXT__;
            }
            // inject component styles
            if (style) {
                style.call(this, createInjectorSSR(context));
            }
            // register component module identifier for async chunk inference
            if (context && context._registeredComponents) {
                context._registeredComponents.add(moduleIdentifier);
            }
        };
        // used by ssr in case component is cached and beforeCreate
        // never gets called
        options._ssrRegister = hook;
    }
    else if (style) {
        hook = shadowMode
            ? function (context) {
                style.call(this, createInjectorShadow(context, this.$root.$options.shadowRoot));
            }
            : function (context) {
                style.call(this, createInjector(context));
            };
    }
    if (hook) {
        if (options.functional) {
            // register for functional component in vue file
            const originalRender = options.render;
            options.render = function renderWithStyleInjection(h, context) {
                hook.call(context);
                return originalRender(h, context);
            };
        }
        else {
            // inject component registration as beforeCreate hook
            const existing = options.beforeCreate;
            options.beforeCreate = existing ? [].concat(existing, hook) : [hook];
        }
    }
    return script;
}

/* script */
const __vue_script__$5 = script$5;

/* template */
var __vue_render__$5 = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c("div", { staticClass: "related-rule recent-change" }, [
    _c(
      "a",
      {
        staticClass: "related-rule-title",
        attrs: {
          href: _vm.html_url,
          target: "_blank",
          rel: "noopener noreferrer"
        }
      },
      [
        _c("span", { staticClass: "link-heading" }, [
          _c("span", { class: _vm.getClassList }, [
            _vm._v(_vm._s(_vm.expandedType))
          ]),
          _vm._v(" "),
          _vm.publication_date
            ? _c("span", { staticClass: "recent-date" }, [
                _vm._v(_vm._s(_vm._f("formatDate")(_vm.publication_date)))
              ])
            : _vm._e(),
          _vm._v("\n            | "),
          _c("span", { staticClass: "recent-fr" }, [
            _vm._v(_vm._s(_vm.citation))
          ])
        ]),
        _vm._v(" "),
        _c("div", { staticClass: "recent-title" }, [_vm._v(_vm._s(_vm.title))])
      ]
    )
  ])
};
var __vue_staticRenderFns__$5 = [];
__vue_render__$5._withStripped = true;

  /* style */
  const __vue_inject_styles__$5 = undefined;
  /* scoped */
  const __vue_scope_id__$5 = undefined;
  /* module identifier */
  const __vue_module_identifier__$5 = undefined;
  /* functional template */
  const __vue_is_functional_template__$5 = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__$5 = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__$5, staticRenderFns: __vue_staticRenderFns__$5 },
    __vue_inject_styles__$5,
    __vue_script__$5,
    __vue_scope_id__$5,
    __vue_is_functional_template__$5,
    __vue_module_identifier__$5,
    false,
    undefined,
    undefined,
    undefined
  );

//
//
//
//
//
//

var script$4 = {
  name: 'show-more-button',
  props: {
    count: {
      type: Number,
      default: 1
    },
    showMore: { type: Function },
  },
  data() {
    return {
      toggle: false,
    }
  },
  computed: {
    buttonText(){
      return this.toggle ? '- Show Less' : '+ Show More';
    }
  },
  methods: {
    toggleButton() {
      this.toggle = !this.toggle;
    }
  }
};

/* script */
const __vue_script__$4 = script$4;

/* template */
var __vue_render__$4 = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c(
    "button",
    {
      staticClass: "show-more-button",
      on: {
        click: function($event) {
          _vm.showMore(), _vm.toggleButton();
        }
      }
    },
    [
      _c("b", [_vm._v(_vm._s(_vm.buttonText))]),
      _vm._v(" (" + _vm._s(_vm.count) + ")\n")
    ]
  )
};
var __vue_staticRenderFns__$4 = [];
__vue_render__$4._withStripped = true;

  /* style */
  const __vue_inject_styles__$4 = undefined;
  /* scoped */
  const __vue_scope_id__$4 = undefined;
  /* module identifier */
  const __vue_module_identifier__$4 = undefined;
  /* functional template */
  const __vue_is_functional_template__$4 = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__$4 = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__$4, staticRenderFns: __vue_staticRenderFns__$4 },
    __vue_inject_styles__$4,
    __vue_script__$4,
    __vue_scope_id__$4,
    __vue_is_functional_template__$4,
    __vue_module_identifier__$4,
    false,
    undefined,
    undefined,
    undefined
  );

//
var script$3 = {
    name: 'related-rule-list',

    components: {
        RelatedRule: __vue_component__$5,
        ShowMoreButton: __vue_component__$4
    },

    props: {
        rules: Array,
        limit: {
          type: Number,
          default: 5
        },
        title: {
          type: String,
        }

    },

    computed: {
        limitedRules() {
            if (this.limitedList) {
                return this.rules.slice(0, this.limit);
            }
            return this.rules;
        },
        rulesCount() {
            return this.rules.length;
        },
    },

    data() {
      return {
          limitedList: true,
      };
    },

    methods: {
        showMore() {
            this.limitedList = !this.limitedList;
        },
    },

    filters: {

    },
};

/* script */
const __vue_script__$3 = script$3;

/* template */
var __vue_render__$3 = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _vm.rules.length
    ? _c(
        "div",
        { staticClass: "related-rule-list" },
        [
          _vm._l(_vm.limitedRules, function(rule, index) {
            return _c("related-rule", {
              key: index,
              attrs: {
                title: rule.title,
                type: rule.type,
                citation: rule.citation,
                publication_date: rule.publication_date,
                document_number: rule.document_number,
                html_url: rule.html_url,
                action: rule.action
              }
            })
          }),
          _vm._v(" "),
          _vm.rules.length > _vm.limit
            ? _c("show-more-button", {
                attrs: { showMore: _vm.showMore, count: _vm.rules.length }
              })
            : _vm._e()
        ],
        2
      )
    : _c("div", { staticClass: "show-more-inactive" }, [
        _vm._v(
          "No " +
            _vm._s(_vm.title) +
            " found in the Federal Register from 1994 to present."
        )
      ])
};
var __vue_staticRenderFns__$3 = [];
__vue_render__$3._withStripped = true;

  /* style */
  const __vue_inject_styles__$3 = undefined;
  /* scoped */
  const __vue_scope_id__$3 = undefined;
  /* module identifier */
  const __vue_module_identifier__$3 = undefined;
  /* functional template */
  const __vue_is_functional_template__$3 = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__$3 = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__$3, staticRenderFns: __vue_staticRenderFns__$3 },
    __vue_inject_styles__$3,
    __vue_script__$3,
    __vue_scope_id__$3,
    __vue_is_functional_template__$3,
    __vue_module_identifier__$3,
    false,
    undefined,
    undefined,
    undefined
  );

//
//
//
//
//
//
//
//
//
//
//

var script$2 = {
    name: "collapsible",

    created: function () {
        requestAnimationFrame(() => {
            this.visible = this.state === "expanded";
            if (!this.visible) {
                this.$refs.target.classList.add("display-none");
            }
        });
        this.$root.$on("collapse-toggle", this.toggle);
    },

    mounted: function () {
        window.addEventListener("resize", this.resize);
        window.addEventListener("transitionend", this.toggleDisplay);
    },

    destroyed: function () {
        window.removeEventListener("resize", this.resize);
        window.removeEventListener("transitionend", this.toggleDisplay);
    },

    props: {
        name: {
            type: String,
            required: true,
        },
        state: {
            //expanded or collapsed
            type: String,
            required: true,
        },
        transition: {
            type: String,
            required: false,
            default: "0.5s",
        },
    },

    data: function () {
        return {
            name: this.name,
            height: "auto",
            visible: false,
            styles: {
                overflow: "hidden",
                transition: this.transition,
            },
        };
    },

    computed: {
        heightStyle: function () {
            return { height: this.height }
        },
    },

    methods: {
        resize: function (e) {
            this.computeHeight();
        },
        toggleDisplay: function (e) {
            if (this.visible) {
                this.$refs.target.style.height = "auto";
            }
            else {
                this.$refs.target.classList.add("display-none");
            }
        },
        toggle: function (target) {
            if (this.name === target) {
                this.$refs.target.classList.remove("display-none");
                requestAnimationFrame(() => {
                    this.computeHeight();
                    requestAnimationFrame(() => {
                        this.visible = !this.visible;
                    });
                });
            }
        },
        getStyle: function () {
            return window.getComputedStyle(this.$refs.target);
        },
        setProps: function (visibility, display, position, height) {
            this.$refs.target.style.visibility = visibility;
            this.$refs.target.style.display = display;
            this.$refs.target.style.position = position;
            this.$refs.target.style.height = height;
        },
        _computeHeight: function () {
            if (this.getStyle().display === "none") {
                return "auto";
            }

            this.$refs.target.classList.remove("invisible");

            this.setProps("hidden", "block", "absolute", "auto");

            const height = this.getStyle().height;

            this.setProps(null, null, null, height);
            if (!this.visible) {
                this.$refs.target.classList.add("invisible");
            }
            return height;
        },
        computeHeight: function () {
            this.height = this._computeHeight();
        },
    },
};

/* script */
const __vue_script__$2 = script$2;

/* template */
var __vue_render__$2 = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c(
    "div",
    {
      ref: "target",
      class: { invisible: !_vm.visible },
      style: [_vm.styles, _vm.sizeStyle],
      attrs: { "data-test": _vm.name }
    },
    [_vm._t("default")],
    2
  )
};
var __vue_staticRenderFns__$2 = [];
__vue_render__$2._withStripped = true;

  /* style */
  const __vue_inject_styles__$2 = undefined;
  /* scoped */
  const __vue_scope_id__$2 = undefined;
  /* module identifier */
  const __vue_module_identifier__$2 = undefined;
  /* functional template */
  const __vue_is_functional_template__$2 = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__$2 = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__$2, staticRenderFns: __vue_staticRenderFns__$2 },
    __vue_inject_styles__$2,
    __vue_script__$2,
    __vue_scope_id__$2,
    __vue_is_functional_template__$2,
    __vue_module_identifier__$2,
    false,
    undefined,
    undefined,
    undefined
  );

//
//
//
//
//
//
//
//
//
//
//
//
//
//

var script$1 = {
    name: "collapse-button",

    created: function () {
        this.visible = this.state === "expanded";
        this.$root.$on("collapse-toggle", this.toggle);
    },

    props: {
        name: {
            type: String,
            required: true,
        },
        state: {
            //expanded or collapsed
            type: String,
            required: true,
        },
        'keep-contents-on-toggle': {
            type: Boolean,
            required: false,
            default: false,
        },
    },

    data: function () {
        return {
            name: this.name,
            visible: true,
        };
    },

    methods: {
        click: function (event) {
            this.$root.$emit("collapse-toggle", this.name);
        },
        toggle: function (target) {
            if (this.name === target) {
                this.visible = !this.visible;
            }
        },
    },
};

/* script */
const __vue_script__$1 = script$1;

/* template */
var __vue_render__$1 = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c(
    "button",
    {
      staticClass: "collapsible-title",
      class: { visible: _vm.visible },
      attrs: {
        "data-test": _vm.name,
        "aria-label": _vm.visible
          ? "collapse " + _vm.name
          : "expand " + _vm.name
      },
      on: { click: _vm.click }
    },
    [
      _vm.visible && !_vm.keepContentsOnToggle
        ? _vm._t("expanded", [_vm._v("Hide")])
        : _vm._e(),
      _vm._v(" "),
      !_vm.visible && !_vm.keepContentsOnToggle
        ? _vm._t("collapsed", [_vm._v("Show")])
        : _vm._e(),
      _vm._v(" "),
      _vm.keepContentsOnToggle
        ? _vm._t("contents", [_vm._v("Click here")])
        : _vm._e()
    ],
    2
  )
};
var __vue_staticRenderFns__$1 = [];
__vue_render__$1._withStripped = true;

  /* style */
  const __vue_inject_styles__$1 = undefined;
  /* scoped */
  const __vue_scope_id__$1 = undefined;
  /* module identifier */
  const __vue_module_identifier__$1 = undefined;
  /* functional template */
  const __vue_is_functional_template__$1 = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__$1 = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__$1, staticRenderFns: __vue_staticRenderFns__$1 },
    __vue_inject_styles__$1,
    __vue_script__$1,
    __vue_scope_id__$1,
    __vue_is_functional_template__$1,
    __vue_module_identifier__$1,
    false,
    undefined,
    undefined,
    undefined
  );

//

var script = {
    components: {
      Collapsible: __vue_component__$2,
      RelatedRuleList: __vue_component__$3,
      CollapseButton: __vue_component__$1,
    },

    props: {
        title: {
            type: String,
            required: true,
        },
        part: {
            type: String,
            required: true,
        },
        limit: {
            type: Number,
            default: 5,
        },
        activeCategory: {
          type: String,
          default: ''
        },
        categoryList: {
          type: Array,
          default: ['FINAL', 'PROPOSED', 'RFI']
        },
        categories: {
          type: Object,
          default: {
            FINAL: {
              getRules: (rules) => {
                return rules.filter(rule => {
                      return rule.type === 'Rule'
                    }
                )
              },
              title: "Final Rules"
            },
            PROPOSED: {
              getRules: (rules) => {
                return rules.filter(rule => {
                      return rule.type === 'Proposed Rule' && rule.action === "Proposed rule."
                    }
                )
              },
              title: "Notices of Proposed Rulemaking"
            },
            RFI: {
              getRules: (rules) => {
                return rules.filter(rule => {
                      return rule.type === 'Proposed Rule' && rule.action === "Request for information."
                    }
                )
              },
              title: "Requests for Information"
            }
          }
        },

    },

    data() {
        return {
            rules: [],
            limitedList: true,
        };
    },

    computed: {

    },

    async created() {
        this.rules = await this.fetch_rules(this.title, this.part);
    },

    methods: {
        async fetch_rules(title, part) {
          let url = `https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=abstract&fields[]=citation&fields[]=correction_of&fields[]=action&fields[]=dates&fields[]=docket_id&fields[]=docket_ids&fields[]=document_number&fields[]=effective_on&fields[]=html_url&fields[]=publication_date&fields[]=regulation_id_number_info&fields[]=regulation_id_numbers&fields[]=title&order=newest&conditions[cfr][title]=${title}&conditions[cfr][part]=${part}`;
          let results = [];
          while(url){
            const response = await fetch(url);
            const rules = await response.json();
            results = results.concat(rules.results);
            url = rules.next_page_url;
          }
          return results

        },
        showCategory(category) {
          category === this.activeCategory ? this.activeCategory = '': this.activeCategory = category;
        },
        buttonClass(category){
          return this.categories[category].getRules(this.rules).length > 0 ? "show-more-button": "show-more-button show-more-inactive"
        },
        getRules(category){
          return this.categories[category].getRules(this.rules)
        }

    },
};

/* script */
const __vue_script__ = script;

/* template */
var __vue_render__ = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c(
    "div",
    _vm._l(_vm.categoryList, function(category) {
      return _c("div", [
        _c(
          "div",
          { staticClass: "category" },
          [
            _c("collapse-button", {
              staticClass: "related-rules-title",
              class: { category: category },
              attrs: { name: category, state: "collapsed" },
              scopedSlots: _vm._u(
                [
                  {
                    key: "expanded",
                    fn: function() {
                      return [
                        _vm._v(_vm._s(_vm.categories[category].title) + " "),
                        _c("i", {
                          staticClass: "fa fa-chevron-up category-toggle"
                        })
                      ]
                    },
                    proxy: true
                  },
                  {
                    key: "collapsed",
                    fn: function() {
                      return [
                        _vm._v(_vm._s(_vm.categories[category].title) + " "),
                        _c("i", {
                          staticClass: "fa fa-chevron-down category-toggle"
                        })
                      ]
                    },
                    proxy: true
                  }
                ],
                null,
                true
              )
            }),
            _vm._v(" "),
            _c(
              "collapsible",
              {
                attrs: {
                  name: category,
                  state:
                    _vm.activeCategory === category ? "expanded" : "collapsed"
                }
              },
              [
                _c("related-rule-list", {
                  attrs: {
                    rules: _vm.getRules(category),
                    limit: _vm.limit,
                    title: _vm.categories[category].title
                  }
                })
              ],
              1
            )
          ],
          1
        )
      ])
    }),
    0
  )
};
var __vue_staticRenderFns__ = [];
__vue_render__._withStripped = true;

  /* style */
  const __vue_inject_styles__ = undefined;
  /* scoped */
  const __vue_scope_id__ = undefined;
  /* module identifier */
  const __vue_module_identifier__ = undefined;
  /* functional template */
  const __vue_is_functional_template__ = false;
  /* style inject */
  
  /* style inject SSR */
  
  /* style inject shadow dom */
  

  
  const __vue_component__ = /*#__PURE__*/normalizeComponent(
    { render: __vue_render__, staticRenderFns: __vue_staticRenderFns__ },
    __vue_inject_styles__,
    __vue_script__,
    __vue_scope_id__,
    __vue_is_functional_template__,
    __vue_module_identifier__,
    false,
    undefined,
    undefined,
    undefined
  );

export default __vue_component__;
//# sourceMappingURL=RelatedRules.js.map
