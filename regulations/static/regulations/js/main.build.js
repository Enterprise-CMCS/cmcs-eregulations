(function (Vue) {
  'use strict';

  function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e : { 'default': e }; }

  var Vue__default = /*#__PURE__*/_interopDefaultLegacy(Vue);

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

  var script$6$1 = {
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
          "keep-contents-on-toggle": {
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

  function normalizeComponent$5(template, style, script, scopeId, isFunctionalTemplate, moduleIdentifier /* server only */, shadowMode, createInjector, createInjectorSSR, createInjectorShadow) {
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
  const __vue_script__$6$1 = script$6$1;

  /* template */
  var __vue_render__$6$1 = function() {
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
  var __vue_staticRenderFns__$6$1 = [];
  __vue_render__$6$1._withStripped = true;

    /* style */
    const __vue_inject_styles__$6$1 = undefined;
    /* scoped */
    const __vue_scope_id__$6$1 = undefined;
    /* module identifier */
    const __vue_module_identifier__$6$1 = undefined;
    /* functional template */
    const __vue_is_functional_template__$6$1 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$6$1 = /*#__PURE__*/normalizeComponent$5(
      { render: __vue_render__$6$1, staticRenderFns: __vue_staticRenderFns__$6$1 },
      __vue_inject_styles__$6$1,
      __vue_script__$6$1,
      __vue_scope_id__$6$1,
      __vue_is_functional_template__$6$1,
      __vue_module_identifier__$6$1,
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

  var script$5$1 = {
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

      methods: {
          resize: function (e) {
              this.computeHeight();
          },
          toggleDisplay: function (e) {
              if (this.visible) {
                  this.$refs.target.style.height = "auto";
              } else {
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
  const __vue_script__$5$1 = script$5$1;

  /* template */
  var __vue_render__$5$1 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c(
      "div",
      {
        ref: "target",
        class: { invisible: !_vm.visible },
        style: [_vm.styles],
        attrs: { "data-test": _vm.name }
      },
      [_vm._t("default")],
      2
    )
  };
  var __vue_staticRenderFns__$5$1 = [];
  __vue_render__$5$1._withStripped = true;

    /* style */
    const __vue_inject_styles__$5$1 = undefined;
    /* scoped */
    const __vue_scope_id__$5$1 = undefined;
    /* module identifier */
    const __vue_module_identifier__$5$1 = undefined;
    /* functional template */
    const __vue_is_functional_template__$5$1 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$5$1 = /*#__PURE__*/normalizeComponent$5(
      { render: __vue_render__$5$1, staticRenderFns: __vue_staticRenderFns__$5$1 },
      __vue_inject_styles__$5$1,
      __vue_script__$5$1,
      __vue_scope_id__$5$1,
      __vue_is_functional_template__$5$1,
      __vue_module_identifier__$5$1,
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
  //

  var script$4$1 = {
      name: "simple-spinner",

      props: {
          size: {
              type: String,
              default: "medium",
          },
          filled: {
              type: Boolean,
              default: false,
          },
      },

      computed: {
          spinnerClasses() {
              return {
                  "ds-c-spinner--filled": this.filled,
                  "ds-c-spinner--small": this.size === "small",
                  "ds-c-spinner--big": this.size === "large",
              };
          },

          spinnerStyles() {
              return {
                  margin: this.size === "small" ? "4px" : "8px",
              };
          },
      },
  };

  /* script */
  const __vue_script__$4$1 = script$4$1;

  /* template */
  var __vue_render__$4$1 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c(
      "div",
      {
        staticClass:
          "ds-u-display--flex ds-u-justify-content--center ds-u-align-items--center"
      },
      [
        _c(
          "span",
          {
            staticClass: "ds-c-spinner",
            class: _vm.spinnerClasses,
            style: _vm.spinnerStyles,
            attrs: { role: "status" }
          },
          [
            _c("span", { staticClass: "ds-u-visibility--screen-reader" }, [
              _vm._v("Loading")
            ])
          ]
        )
      ]
    )
  };
  var __vue_staticRenderFns__$4$1 = [];
  __vue_render__$4$1._withStripped = true;

    /* style */
    const __vue_inject_styles__$4$1 = undefined;
    /* scoped */
    const __vue_scope_id__$4$1 = undefined;
    /* module identifier */
    const __vue_module_identifier__$4$1 = undefined;
    /* functional template */
    const __vue_is_functional_template__$4$1 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$4$1 = /*#__PURE__*/normalizeComponent$5(
      { render: __vue_render__$4$1, staticRenderFns: __vue_staticRenderFns__$4$1 },
      __vue_inject_styles__$4$1,
      __vue_script__$4$1,
      __vue_scope_id__$4$1,
      __vue_is_functional_template__$4$1,
      __vue_module_identifier__$4$1,
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
  //
  //
  //
  //
  //
  //

  var script$3$1 = {
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

  /* script */
  const __vue_script__$3$1 = script$3$1;

  /* template */
  var __vue_render__$3$1 = function() {
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
  var __vue_staticRenderFns__$3$1 = [];
  __vue_render__$3$1._withStripped = true;

    /* style */
    const __vue_inject_styles__$3$1 = undefined;
    /* scoped */
    const __vue_scope_id__$3$1 = undefined;
    /* module identifier */
    const __vue_module_identifier__$3$1 = undefined;
    /* functional template */
    const __vue_is_functional_template__$3$1 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$3$1 = /*#__PURE__*/normalizeComponent$5(
      { render: __vue_render__$3$1, staticRenderFns: __vue_staticRenderFns__$3$1 },
      __vue_inject_styles__$3$1,
      __vue_script__$3$1,
      __vue_scope_id__$3$1,
      __vue_is_functional_template__$3$1,
      __vue_module_identifier__$3$1,
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

  var script$2$2 = {
      name: "show-more-button",
      props: {
          count: {
              type: Number,
              default: 1,
          },
          buttonText: {
              type: String,
              required: true
          }
      },
  };

  /* script */
  const __vue_script__$2$2 = script$2$2;

  /* template */
  var __vue_render__$2$2 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c("div", { staticClass: "show-more-button" }, [
      _c("b", [_vm._v(_vm._s(_vm.buttonText))]),
      _vm._v(" (" + _vm._s(_vm.count) + ")\n")
    ])
  };
  var __vue_staticRenderFns__$2$2 = [];
  __vue_render__$2$2._withStripped = true;

    /* style */
    const __vue_inject_styles__$2$2 = undefined;
    /* scoped */
    const __vue_scope_id__$2$2 = undefined;
    /* module identifier */
    const __vue_module_identifier__$2$2 = undefined;
    /* functional template */
    const __vue_is_functional_template__$2$2 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$2$2 = /*#__PURE__*/normalizeComponent$5(
      { render: __vue_render__$2$2, staticRenderFns: __vue_staticRenderFns__$2$2 },
      __vue_inject_styles__$2$2,
      __vue_script__$2$2,
      __vue_scope_id__$2$2,
      __vue_is_functional_template__$2$2,
      __vue_module_identifier__$2$2,
      false,
      undefined,
      undefined,
      undefined
    );

  //

  var script$1$2 = {
      name: "related-rule-list",

      components: {
          RelatedRule: __vue_component__$3$1,
          ShowMoreButton: __vue_component__$2$2,
          CollapseButton: __vue_component__$6$1,
          Collapsible: __vue_component__$5$1,
      },

      props: {
          rules: Array,
          limit: {
              type: Number,
              default: 5,
          },
          title: {
              type: String,
          },
      },

      computed: {
          limitedRules() {
              return this.rules.slice(0, this.limit);
          },
          additionalRules() {
              return this.rules.slice(this.limit);
          },
          rulesCount() {
              return this.rules.length;
          },
          showMoreNeeded() {
              return this.rulesCount > this.limit;
          }
      },

      data() {
          return {
              limitedList: true,
              innerName: Math.random()
                  .toString(36)
                  .replace(/[^a-z]+/g, ""),
          };
      },

      methods: {
          showMore() {
              this.limitedList = !this.limitedList;
          },
      },

      filters: {},
  };

  /* script */
  const __vue_script__$1$2 = script$1$2;

  /* template */
  var __vue_render__$1$2 = function() {
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
            _vm.showMoreNeeded && _vm.rulesCount > 10
              ? _c("collapse-button", {
                  staticClass: "category-title",
                  class: { subcategory: _vm.subcategory },
                  attrs: { name: _vm.innerName, state: "collapsed" },
                  scopedSlots: _vm._u(
                    [
                      {
                        key: "expanded",
                        fn: function() {
                          return [
                            _c("show-more-button", {
                              attrs: {
                                buttonText: "- Show Less",
                                count: _vm.rules.length
                              }
                            })
                          ]
                        },
                        proxy: true
                      },
                      {
                        key: "collapsed",
                        fn: function() {
                          return [
                            _c("show-more-button", {
                              attrs: {
                                buttonText: "+ Show More",
                                count: _vm.rules.length
                              }
                            })
                          ]
                        },
                        proxy: true
                      }
                    ],
                    null,
                    false,
                    66893211
                  )
                })
              : _vm._e(),
            _vm._v(" "),
            _c(
              "collapsible",
              {
                staticClass: "category-content additional-rules",
                attrs: { name: _vm.innerName, state: "collapsed" }
              },
              [
                _vm._l(_vm.additionalRules, function(rule, index) {
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
                _vm.showMoreNeeded && _vm.rulesCount > 0
                  ? _c("collapse-button", {
                      staticClass: "category-title",
                      class: { subcategory: _vm.subcategory },
                      attrs: { name: _vm.innerName, state: "collapsed" },
                      scopedSlots: _vm._u(
                        [
                          {
                            key: "expanded",
                            fn: function() {
                              return [
                                _c("show-more-button", {
                                  attrs: {
                                    buttonText: "- Show Less",
                                    count: _vm.rules.length
                                  }
                                })
                              ]
                            },
                            proxy: true
                          },
                          {
                            key: "collapsed",
                            fn: function() {
                              return [
                                _c("show-more-button", {
                                  attrs: {
                                    buttonText: "+ Show More",
                                    count: _vm.rules.length
                                  }
                                })
                              ]
                            },
                            proxy: true
                          }
                        ],
                        null,
                        false,
                        66893211
                      )
                    })
                  : _vm._e()
              ],
              2
            )
          ],
          2
        )
      : _c("div", { staticClass: "show-more-inactive" }, [
          _vm._v(
            "\n    No " +
              _vm._s(_vm.title) +
              " found in the Federal Register from 1994 to present.\n"
          )
        ])
  };
  var __vue_staticRenderFns__$1$2 = [];
  __vue_render__$1$2._withStripped = true;

    /* style */
    const __vue_inject_styles__$1$2 = undefined;
    /* scoped */
    const __vue_scope_id__$1$2 = undefined;
    /* module identifier */
    const __vue_module_identifier__$1$2 = undefined;
    /* functional template */
    const __vue_is_functional_template__$1$2 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$1$2 = /*#__PURE__*/normalizeComponent$5(
      { render: __vue_render__$1$2, staticRenderFns: __vue_staticRenderFns__$1$2 },
      __vue_inject_styles__$1$2,
      __vue_script__$1$2,
      __vue_scope_id__$1$2,
      __vue_is_functional_template__$1$2,
      __vue_module_identifier__$1$2,
      false,
      undefined,
      undefined,
      undefined
    );

  //

  var script$b = {
      components: {
          CollapseButton: __vue_component__$6$1,
          Collapsible: __vue_component__$5$1,
          RelatedRuleList: __vue_component__$1$2,
          SimpleSpinner: __vue_component__$4$1,
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
              default: "",
          },
          categoryList: {
              type: Array,
              default: ["FINAL", "PROPOSED", "RFI"],
          },
          categories: {
              type: Object,
              default: {
                  FINAL: {
                      getRules: (rules) => {
                          return rules.filter((rule) => {
                              return rule.type === "Rule";
                          });
                      },
                      title: "Final Rules",
                  },
                  PROPOSED: {
                      getRules: (rules) => {
                          return rules.filter((rule) => {
                              return (
                                  rule.type === "Proposed Rule" &&
                                  rule.action === "Proposed rule."
                              );
                          });
                      },
                      title: "Notices of Proposed Rulemaking",
                  },
                  RFI: {
                      getRules: (rules) => {
                          return rules.filter((rule) => {
                              return (
                                  rule.type === "Proposed Rule" &&
                                  rule.action === "Request for information."
                              );
                          });
                      },
                      title: "Requests for Information",
                  },
              },
          },
      },

      data() {
          return {
              isFetching: true,
              limitedList: true,
              rules: [],
          };
      },

      computed: {},

      created() {
          this.fetch_rules(this.title, this.part);
      },

      methods: {
          async fetch_rules(title, part) {
              let url = `https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=abstract&fields[]=citation&fields[]=correction_of&fields[]=action&fields[]=dates&fields[]=docket_id&fields[]=docket_ids&fields[]=document_number&fields[]=effective_on&fields[]=html_url&fields[]=publication_date&fields[]=regulation_id_number_info&fields[]=regulation_id_numbers&fields[]=title&order=newest&conditions[cfr][title]=${title}&conditions[cfr][part]=${part}`;
              let results = [];
              try {
                  while (url) {
                      const response = await fetch(url);
                      const rules = await response.json();
                      results = results.concat(rules.results ?? []);
                      url = rules.next_page_url;
                  }
                  this.rules = results;
              } catch (error) {
                  console.error(error);
              } finally {
                  this.isFetching = false;
              }
          },
          showCategory(category) {
              category === this.activeCategory
                  ? (this.activeCategory = "")
                  : (this.activeCategory = category);
          },
          buttonClass(category) {
              return this.categories[category].getRules(this.rules).length > 0
                  ? "show-more-button"
                  : "show-more-button show-more-inactive";
          },
          getRules(category) {
              return this.categories[category].getRules(this.rules);
          },
      },
  };

  /* script */
  const __vue_script__$b = script$b;

  /* template */
  var __vue_render__$b = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c(
      "div",
      _vm._l(_vm.categoryList, function(category, index) {
        return _c("div", { key: index }, [
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
                          _vm._v(
                            _vm._s(_vm.categories[category].title) +
                              "\n                    "
                          ),
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
                          _vm._v(
                            _vm._s(_vm.categories[category].title) +
                              "\n                    "
                          ),
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
                  _vm.isFetching
                    ? [_c("simple-spinner", { attrs: { size: "small" } })]
                    : [
                        _c("related-rule-list", {
                          attrs: {
                            rules: _vm.getRules(category),
                            limit: _vm.limit,
                            title: _vm.categories[category].title
                          }
                        })
                      ]
                ],
                2
              )
            ],
            1
          )
        ])
      }),
      0
    )
  };
  var __vue_staticRenderFns__$b = [];
  __vue_render__$b._withStripped = true;

    /* style */
    const __vue_inject_styles__$b = undefined;
    /* scoped */
    const __vue_scope_id__$b = undefined;
    /* module identifier */
    const __vue_module_identifier__$b = undefined;
    /* functional template */
    const __vue_is_functional_template__$b = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$b = /*#__PURE__*/normalizeComponent$5(
      { render: __vue_render__$b, staticRenderFns: __vue_staticRenderFns__$b },
      __vue_inject_styles__$b,
      __vue_script__$b,
      __vue_scope_id__$b,
      __vue_is_functional_template__$b,
      __vue_module_identifier__$b,
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

  var script$a = {
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

      methods: {
          resize: function (e) {
              this.computeHeight();
          },
          toggleDisplay: function (e) {
              if (this.visible) {
                  this.$refs.target.style.height = "auto";
              } else {
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

  function normalizeComponent$4(template, style, script, scopeId, isFunctionalTemplate, moduleIdentifier /* server only */, shadowMode, createInjector, createInjectorSSR, createInjectorShadow) {
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
  const __vue_script__$a = script$a;

  /* template */
  var __vue_render__$a = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c(
      "div",
      {
        ref: "target",
        class: { invisible: !_vm.visible },
        style: [_vm.styles],
        attrs: { "data-test": _vm.name }
      },
      [_vm._t("default")],
      2
    )
  };
  var __vue_staticRenderFns__$a = [];
  __vue_render__$a._withStripped = true;

    /* style */
    const __vue_inject_styles__$a = undefined;
    /* scoped */
    const __vue_scope_id__$a = undefined;
    /* module identifier */
    const __vue_module_identifier__$a = undefined;
    /* functional template */
    const __vue_is_functional_template__$a = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$a = /*#__PURE__*/normalizeComponent$4(
      { render: __vue_render__$a, staticRenderFns: __vue_staticRenderFns__$a },
      __vue_inject_styles__$a,
      __vue_script__$a,
      __vue_scope_id__$a,
      __vue_is_functional_template__$a,
      __vue_module_identifier__$a,
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
  //
  //
  //
  //

  var script$9 = {
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
          "keep-contents-on-toggle": {
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

  function normalizeComponent$3(template, style, script, scopeId, isFunctionalTemplate, moduleIdentifier /* server only */, shadowMode, createInjector, createInjectorSSR, createInjectorShadow) {
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
  const __vue_script__$9 = script$9;

  /* template */
  var __vue_render__$9 = function() {
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
  var __vue_staticRenderFns__$9 = [];
  __vue_render__$9._withStripped = true;

    /* style */
    const __vue_inject_styles__$9 = undefined;
    /* scoped */
    const __vue_scope_id__$9 = undefined;
    /* module identifier */
    const __vue_module_identifier__$9 = undefined;
    /* functional template */
    const __vue_is_functional_template__$9 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$9 = /*#__PURE__*/normalizeComponent$3(
      { render: __vue_render__$9, staticRenderFns: __vue_staticRenderFns__$9 },
      __vue_inject_styles__$9,
      __vue_script__$9,
      __vue_scope_id__$9,
      __vue_is_functional_template__$9,
      __vue_module_identifier__$9,
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
  //

  var script$7 = {
      name: "simple-spinner",

      props: {
          size: {
              type: String,
              default: "medium",
          },
          filled: {
              type: Boolean,
              default: false,
          },
      },

      computed: {
          spinnerClasses() {
              return {
                  "ds-c-spinner--filled": this.filled,
                  "ds-c-spinner--small": this.size === "small",
                  "ds-c-spinner--big": this.size === "large",
              };
          },

          spinnerStyles() {
              return {
                  margin: this.size === "small" ? "4px" : "8px",
              };
          },
      },
  };

  function normalizeComponent$2(template, style, script, scopeId, isFunctionalTemplate, moduleIdentifier /* server only */, shadowMode, createInjector, createInjectorSSR, createInjectorShadow) {
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
  const __vue_script__$7 = script$7;

  /* template */
  var __vue_render__$7 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c(
      "div",
      {
        staticClass:
          "ds-u-display--flex ds-u-justify-content--center ds-u-align-items--center"
      },
      [
        _c(
          "span",
          {
            staticClass: "ds-c-spinner",
            class: _vm.spinnerClasses,
            style: _vm.spinnerStyles,
            attrs: { role: "status" }
          },
          [
            _c("span", { staticClass: "ds-u-visibility--screen-reader" }, [
              _vm._v("Loading")
            ])
          ]
        )
      ]
    )
  };
  var __vue_staticRenderFns__$7 = [];
  __vue_render__$7._withStripped = true;

    /* style */
    const __vue_inject_styles__$7 = undefined;
    /* scoped */
    const __vue_scope_id__$7 = undefined;
    /* module identifier */
    const __vue_module_identifier__$7 = undefined;
    /* functional template */
    const __vue_is_functional_template__$7 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$7 = /*#__PURE__*/normalizeComponent$2(
      { render: __vue_render__$7, staticRenderFns: __vue_staticRenderFns__$7 },
      __vue_inject_styles__$7,
      __vue_script__$7,
      __vue_scope_id__$7,
      __vue_is_functional_template__$7,
      __vue_module_identifier__$7,
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


  var script$6 = {
    name: 'supplemental-content-object',

    props: {
      name: {
        type: String,
        required: true,
      },
      description: {
          type: String,
          required: false,
      },
      date: {
          type: String,
          required: false,
      },
      url: {
        type: String,
        required: true,
      },
    },
    
    filters: {
      formatDate: function(value) {
        const date = new Date(value);
        let options = { year: 'numeric', timeZone: 'UTC' };
        const raw_date = value.split('-');
        if(raw_date.length > 1) {
          options.month = 'long';
        }
        if(raw_date.length > 2) {
          options.day = 'numeric';
        }
        const format = new Intl.DateTimeFormat("en-US", options);
        return format.format(date);
      }
    },

    methods: {
      isBlank: function(str) {
        return (!str || /^\s*$/.test(str));
      },
    },
  };

  /* script */
  const __vue_script__$6 = script$6;

  /* template */
  var __vue_render__$6 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c("div", { staticClass: "supplemental-content" }, [
      _c(
        "a",
        {
          staticClass: "supplemental-content-link",
          attrs: { href: _vm.url, target: "_blank", rel: "noopener noreferrer" }
        },
        [
          _vm.date
            ? _c(
                "span",
                {
                  staticClass: "supplemental-content-date",
                  class: {
                    "supplemental-content-mid-bar": !_vm.isBlank(_vm.name)
                  }
                },
                [_vm._v(_vm._s(_vm._f("formatDate")(_vm.date)))]
              )
            : _vm._e(),
          _vm._v(" "),
          !_vm.isBlank(_vm.name)
            ? _c(
                "span",
                {
                  staticClass: "supplemental-content-title",
                  class: {
                    "supplemental-content-external-link": _vm.isBlank(
                      _vm.description
                    )
                  }
                },
                [_vm._v(_vm._s(_vm.name))]
              )
            : _vm._e(),
          _vm._v(" "),
          !_vm.isBlank(_vm.description)
            ? _c(
                "div",
                {
                  staticClass:
                    "supplemental-content-description supplemental-content-external-link"
                },
                [_vm._v(_vm._s(_vm.description))]
              )
            : _vm._e()
        ]
      )
    ])
  };
  var __vue_staticRenderFns__$6 = [];
  __vue_render__$6._withStripped = true;

    /* style */
    const __vue_inject_styles__$6 = undefined;
    /* scoped */
    const __vue_scope_id__$6 = undefined;
    /* module identifier */
    const __vue_module_identifier__$6 = undefined;
    /* functional template */
    const __vue_is_functional_template__$6 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$6 = /*#__PURE__*/normalizeComponent$2(
      { render: __vue_render__$6, staticRenderFns: __vue_staticRenderFns__$6 },
      __vue_inject_styles__$6,
      __vue_script__$6,
      __vue_scope_id__$6,
      __vue_is_functional_template__$6,
      __vue_module_identifier__$6,
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

  var script$5 = {
      name: "show-more-button",
      props: {
          count: {
              type: Number,
              default: 1,
          },
          buttonText: {
              type: String,
              required: true
          }
      },
  };

  /* script */
  const __vue_script__$5 = script$5;

  /* template */
  var __vue_render__$5 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c("div", { staticClass: "show-more-button" }, [
      _c("b", [_vm._v(_vm._s(_vm.buttonText))]),
      _vm._v(" (" + _vm._s(_vm.count) + ")\n")
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
    

    
    const __vue_component__$5 = /*#__PURE__*/normalizeComponent$2(
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

  var script$4 = {
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
          "keep-contents-on-toggle": {
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
  const __vue_script__$4 = script$4;

  /* template */
  var __vue_render__$4 = function() {
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
    

    
    const __vue_component__$4 = /*#__PURE__*/normalizeComponent$2(
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

  var script$3 = {
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

      methods: {
          resize: function (e) {
              this.computeHeight();
          },
          toggleDisplay: function (e) {
              if (this.visible) {
                  this.$refs.target.style.height = "auto";
              } else {
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
  const __vue_script__$3 = script$3;

  /* template */
  var __vue_render__$3 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c(
      "div",
      {
        ref: "target",
        class: { invisible: !_vm.visible },
        style: [_vm.styles],
        attrs: { "data-test": _vm.name }
      },
      [_vm._t("default")],
      2
    )
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
    

    
    const __vue_component__$3 = /*#__PURE__*/normalizeComponent$2(
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

  var script$2$1 = {
      name: "supplemental-content-list",

      components: {
          SupplementalContentObject: __vue_component__$6,
          ShowMoreButton: __vue_component__$5,
          CollapseButton: __vue_component__$4,
          Collapsible: __vue_component__$3,
      },

      props: {
          supplemental_content: {
              type: Array,
              required: true,
          },
          has_sub_categories: {
              type: Boolean,
              required: true,
          },
          limit: {
              type: Number,
              required: false,
              default: 5,
          },
      },

      data() {
          return {
              innerName: Math.random()
                  .toString(36)
                  .replace(/[^a-z]+/g, ""),
          };
      },

      computed: {
          limitedContent() {
              return this.supplemental_content.slice(0, this.limit);
          },
          additionalContent() {
              return this.supplemental_content.slice(this.limit);
          },
          contentCount() {
              return this.supplemental_content.length;
          },
          showMoreNeeded() {
              return this.contentCount > this.limit;
          },
      },
  };

  /* script */
  const __vue_script__$2$1 = script$2$1;

  /* template */
  var __vue_render__$2$1 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return !_vm.has_sub_categories
      ? _c(
          "div",
          { staticClass: "supplemental-content-list" },
          [
            _vm._l(_vm.limitedContent, function(content, index) {
              return _c("supplemental-content-object", {
                key: index,
                attrs: {
                  name: content.name,
                  description: content.description,
                  date: content.date,
                  url: content.url
                }
              })
            }),
            _vm._v(" "),
            _vm.showMoreNeeded
              ? _c("collapse-button", {
                  staticClass: "category-title show-more",
                  class: { subcategory: _vm.subcategory },
                  attrs: { name: _vm.innerName, state: "collapsed" },
                  scopedSlots: _vm._u(
                    [
                      {
                        key: "expanded",
                        fn: function() {
                          return [
                            _c("show-more-button", {
                              attrs: {
                                buttonText: "- Show Less",
                                count: _vm.contentCount
                              }
                            })
                          ]
                        },
                        proxy: true
                      },
                      {
                        key: "collapsed",
                        fn: function() {
                          return [
                            _c("show-more-button", {
                              attrs: {
                                buttonText: "+ Show More",
                                count: _vm.contentCount
                              }
                            })
                          ]
                        },
                        proxy: true
                      }
                    ],
                    null,
                    false,
                    1539528923
                  )
                })
              : _vm._e(),
            _vm._v(" "),
            _c(
              "collapsible",
              {
                staticClass: "category-content show-more-content",
                attrs: { name: _vm.innerName, state: "collapsed" }
              },
              [
                _vm._l(_vm.additionalContent, function(content, index) {
                  return _c("supplemental-content-object", {
                    key: index,
                    attrs: {
                      name: content.name,
                      description: content.description,
                      date: content.date,
                      url: content.url
                    }
                  })
                }),
                _vm._v(" "),
                _vm.showMoreNeeded && _vm.contentCount > 10
                  ? _c("collapse-button", {
                      staticClass: "category-title show-more",
                      class: { subcategory: _vm.subcategory },
                      attrs: { name: _vm.innerName, state: "collapsed" },
                      scopedSlots: _vm._u(
                        [
                          {
                            key: "expanded",
                            fn: function() {
                              return [
                                _c("show-more-button", {
                                  attrs: {
                                    buttonText: "- Show Less",
                                    count: _vm.contentCount
                                  }
                                })
                              ]
                            },
                            proxy: true
                          },
                          {
                            key: "collapsed",
                            fn: function() {
                              return [
                                _c("show-more-button", {
                                  attrs: {
                                    buttonText: "+ Show More",
                                    count: _vm.contentCount
                                  }
                                })
                              ]
                            },
                            proxy: true
                          }
                        ],
                        null,
                        false,
                        1539528923
                      )
                    })
                  : _vm._e()
              ],
              2
            )
          ],
          2
        )
      : _vm._e()
  };
  var __vue_staticRenderFns__$2$1 = [];
  __vue_render__$2$1._withStripped = true;

    /* style */
    const __vue_inject_styles__$2$1 = undefined;
    /* scoped */
    const __vue_scope_id__$2$1 = undefined;
    /* module identifier */
    const __vue_module_identifier__$2$1 = undefined;
    /* functional template */
    const __vue_is_functional_template__$2$1 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$2$1 = /*#__PURE__*/normalizeComponent$2(
      { render: __vue_render__$2$1, staticRenderFns: __vue_staticRenderFns__$2$1 },
      __vue_inject_styles__$2$1,
      __vue_script__$2$1,
      __vue_scope_id__$2$1,
      __vue_is_functional_template__$2$1,
      __vue_module_identifier__$2$1,
      false,
      undefined,
      undefined,
      undefined
    );

  //

  var script$1$1 = {
      name: "supplemental-content-category",

      components: {
          SupplementalContentList: __vue_component__$2$1,
          CollapseButton: __vue_component__$4,
          Collapsible: __vue_component__$3,
      },

      props: {
          subcategory: {
              type: Boolean,
              required: false,
              default: false,
          },
          name: {
              type: String,
              required: true,
          },
          description: {
              type: String,
              required: true,
          },
          supplemental_content: {
              type: Array,
              required: false,
          },
          sub_categories: {
              type: Array,
              required: false,
          },
      },

      computed: {
          showDescription: function () {
              return this.description && !/^\s*$/.test(this.description);
          },
          has_sub_categories() {
              return this.sub_categories.length;
          },
      },
  };

  /* script */
  const __vue_script__$1$1 = script$1$1;

  /* template */
  var __vue_render__$1$1 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c("div", { staticClass: "supplemental-content-category" }, [
      _c(
        "div",
        { staticClass: "category" },
        [
          _c("collapse-button", {
            staticClass: "category-title",
            class: { subcategory: _vm.subcategory },
            attrs: { name: _vm.name, state: "collapsed" },
            scopedSlots: _vm._u([
              {
                key: "expanded",
                fn: function() {
                  return [
                    _vm._v(_vm._s(_vm.name) + " "),
                    _c("i", { staticClass: "fa fa-chevron-up" })
                  ]
                },
                proxy: true
              },
              {
                key: "collapsed",
                fn: function() {
                  return [
                    _vm._v(_vm._s(_vm.name) + " "),
                    _c("i", { staticClass: "fa fa-chevron-down" })
                  ]
                },
                proxy: true
              }
            ])
          }),
          _vm._v(" "),
          _vm.showDescription
            ? _c("span", { staticClass: "category-description" }, [
                _vm._v(_vm._s(_vm.description))
              ])
            : _vm._e(),
          _vm._v(" "),
          _c(
            "collapsible",
            {
              staticClass: "category-content",
              attrs: { name: _vm.name, state: "collapsed" }
            },
            [
              _vm._l(_vm.sub_categories, function(category, index) {
                return _c("supplemental-content-category", {
                  key: index,
                  attrs: {
                    subcategory: true,
                    name: category.name,
                    description: category.description,
                    supplemental_content: category.supplemental_content,
                    sub_categories: category.sub_categories
                  }
                })
              }),
              _vm._v(" "),
              _c("supplemental-content-list", {
                attrs: {
                  supplemental_content: _vm.supplemental_content,
                  has_sub_categories: _vm.has_sub_categories
                }
              })
            ],
            2
          )
        ],
        1
      )
    ])
  };
  var __vue_staticRenderFns__$1$1 = [];
  __vue_render__$1$1._withStripped = true;

    /* style */
    const __vue_inject_styles__$1$1 = undefined;
    /* scoped */
    const __vue_scope_id__$1$1 = undefined;
    /* module identifier */
    const __vue_module_identifier__$1$1 = undefined;
    /* functional template */
    const __vue_is_functional_template__$1$1 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$1$1 = /*#__PURE__*/normalizeComponent$2(
      { render: __vue_render__$1$1, staticRenderFns: __vue_staticRenderFns__$1$1 },
      __vue_inject_styles__$1$1,
      __vue_script__$1$1,
      __vue_scope_id__$1$1,
      __vue_is_functional_template__$1$1,
      __vue_module_identifier__$1$1,
      false,
      undefined,
      undefined,
      undefined
    );

  //

  var script$8 = {
      components: {
          SupplementalContentCategory: __vue_component__$1$1,
          SimpleSpinner: __vue_component__$7,
      },

      props: {
          api_url: {
              type: String,
              required: true,
          },
          title: {
              type: String,
              required: true,
          },
          part: {
              type: String,
              required: true,
          },
          sections: {
              type: Array,
              required: false,
              default: [],
          },
          subparts: {
              type: Array,
              required: false,
              default: [],
          },
      },

      data() {
          return {
              categories: [],
              isFetching: true,
          };
      },

      created() {
          this.fetch_content(this.title, this.part);
      },

      computed: {
          params_array: function () {
              return [
                  ["sections", this.sections],
                  ["subparts", this.subparts],
              ];
          },
          joined_locations: function () {
              let output = "";
              this.params_array.forEach(function (param) {
                  if (param[1].length > 0) {
                      const queryString = "&" + param[0] + "=";
                      output += queryString + param[1].join(queryString);
                  }
              });
              return output;
          },
      },

      methods: {
          async fetch_content(title, part) {
              try {
                  const response = await fetch(
                      `${this.api_url}title/${title}/part/${part}/supplemental_content?${this.joined_locations}`
                  );
                  const content = await response.json();
                  this.categories = content;
              } catch (error) {
                  console.error(error);
              } finally {
                  this.isFetching = false;
              }
          },
      },
  };

  /* script */
  const __vue_script__$8 = script$8;

  /* template */
  var __vue_render__$8 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c(
      "div",
      { staticClass: "supplemental-content-container" },
      [
        _vm.isFetching
          ? [_c("simple-spinner")]
          : _vm._l(_vm.categories, function(category, index) {
              return _c("supplemental-content-category", {
                key: index,
                attrs: {
                  name: category.name,
                  description: category.description,
                  supplemental_content: category.supplemental_content,
                  sub_categories: category.sub_categories
                }
              })
            })
      ],
      2
    )
  };
  var __vue_staticRenderFns__$8 = [];
  __vue_render__$8._withStripped = true;

    /* style */
    const __vue_inject_styles__$8 = undefined;
    /* scoped */
    const __vue_scope_id__$8 = undefined;
    /* module identifier */
    const __vue_module_identifier__$8 = undefined;
    /* functional template */
    const __vue_is_functional_template__$8 = false;
    /* style inject */
    
    /* style inject SSR */
    
    /* style inject shadow dom */
    

    
    const __vue_component__$8 = /*#__PURE__*/normalizeComponent$2(
      { render: __vue_render__$8, staticRenderFns: __vue_staticRenderFns__$8 },
      __vue_inject_styles__$8,
      __vue_script__$8,
      __vue_scope_id__$8,
      __vue_is_functional_template__$8,
      __vue_module_identifier__$8,
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
  //
  //
  //
  //

  var script$1 = {
      name: "action-button",

      props: {
          actionType: {
              type: String,
              required: true,
          },
          selectedAction: {
              type: String,
              required: true,
          },
          status: {
              type: String,
              required: true,
          },
      },

      computed: {
          selected() {
              return (
                  this.selectedAction === this.actionType &&
                  this.status !== "idle"
              );
          },
          labelState() {
              return this.selected && this.status === "success"
                  ? "copied"
                  : "copy";
          },
          label() {
              return `${this.labelState} ${this.actionType}`;
          },
          buttonClasses() {
              return {
                  "selected-btn": this.selected && this.status === "success",
                  "default-btn": !this.selected,
              };
          },
      },

      methods: {
          handleClick() {
              this.$emit("action-btn-click", {
                  actionType: this.actionType,
              });
          },
      },

      filters: {},
  };

  function normalizeComponent$1(template, style, script, scopeId, isFunctionalTemplate, moduleIdentifier /* server only */, shadowMode, createInjector, createInjectorSSR, createInjectorShadow) {
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
  const __vue_script__$1 = script$1;

  /* template */
  var __vue_render__$1 = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c(
      "button",
      {
        staticClass: "action-btn",
        class: _vm.buttonClasses,
        attrs: { disabled: _vm.selected && this.status === "success" },
        on: { click: _vm.handleClick }
      },
      [
        _vm.selected && this.status === "success"
          ? _c(
              "svg",
              { attrs: { width: "17", height: "17", viewBox: "0 0 17 17" } },
              [
                _c("svg", { attrs: { width: "17", height: "17" } }, [
                  _c("path", {
                    attrs: {
                      "fill-rule": "evenodd",
                      "clip-rule": "evenodd",
                      d:
                        "M8.50007 16C4.36452 16 1 12.6355 1 8.50007C1 4.36452 4.36452 1 8.50007 1C12.6355 1 15.9999 4.36452 15.9999 8.50007C15.9999 12.6355 12.6355 16 8.50007 16ZM8.50007 2.02937C4.93206 2.02937 2.02922 4.93221 2.02922 8.50007C2.02922 12.0681 4.93206 14.9708 8.50007 14.9708C12.0679 14.9708 14.9706 12.0681 14.9706 8.50007C14.9706 4.93221 12.0679 2.02937 8.50007 2.02937Z",
                      fill: "#2A7A3B",
                      stroke: "#2A7A3B",
                      "stroke-width": "0.25"
                    }
                  })
                ]),
                _vm._v(" "),
                _c(
                  "svg",
                  { attrs: { width: "17", height: "17", x: "4", y: "5" } },
                  [
                    _c("path", {
                      attrs: {
                        "fill-rule": "evenodd",
                        "clip-rule": "evenodd",
                        d:
                          "M3.48221 5.98237C3.34562 5.98237 3.21476 5.92812 3.11831 5.83166L1.2191 3.93246C1.01811 3.73161 1.01811 3.40565 1.2191 3.2048C1.4201 3.00366 1.74577 3.00366 1.94676 3.2048L3.48221 4.73996L7.05287 1.1693C7.25357 0.968307 7.57954 0.968307 7.78053 1.1693C7.98152 1.37014 7.98152 1.69611 7.78053 1.89696L3.84597 5.83166C3.74951 5.92812 3.61866 5.98237 3.48221 5.98237Z",
                        fill: "#2A7A3B",
                        stroke: "#2A7A3B",
                        "stroke-width": "0.25"
                      }
                    })
                  ]
                )
              ]
            )
          : _vm._e(),
        _vm._v("\n    " + _vm._s(_vm.label) + "\n")
      ]
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
    

    
    const __vue_component__$1 = /*#__PURE__*/normalizeComponent$1(
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

  const getAnchorY = (el, elType) => {
      if (!el) return 0;

      return elType === "labeled-icon"
          ? el.offsetWidth / 2
          : el.offsetWidth * 0.7;
  };

  const getAnchorX = (el, elType) => {
      if (!el) return 0;

      return parseInt(window.getComputedStyle(el).fontSize, 10) + 20;
  };

  const appendPxSuffix = (int) => `${int}px`;

  const leftWarning = (el) => el.getBoundingClientRect().left < 130;

  var script$2 = {
      name: "copy-btn",

      components: {
          ActionBtn: __vue_component__$1,
      },

      props: {
          btn_type: {
              type: String,
              required: true,
          },
          title: {
              type: String,
              required: true,
          },
          hash: {
              type: String,
              required: true,
          },
          formatted_citation: {
              type: String,
              required: true,
          },
      },

      data() {
          return {
              entered: false,
              clicked: false,
              leftSafe: true,
              anchorY: 0,
              anchorX: 0,
              label: "Copy Link or Citation",
              selectedAction: null,
              copyStatus: "idle",
          };
      },

      computed: {
          ariaLabel() {
              return this.btn_type === "icon"
                  ? `${this.label} for ${this.title}`
                  : false;
          },
          buttonClasses() {
              return {
                  "copy-btn-labeled": this.btn_type === "labeled-icon",
              };
          },
          tooltipClasses() {
              return {
                  "tooltip-caret": this.leftSafe,
                  "tooltip-caret-left": !this.leftSafe,
              };
          },
          tooltipStyles() {
              return {
                  left: this.anchorY,
                  bottom: this.anchorX,
                  transform: `translate(-${this.leftSafe ? 50 : 20}%, 0)`,
              };
          },
      },

      watch: {
          copyStatus: async function (newStatus, oldStatus) {
              if (
                  newStatus === "pending" &&
                  (oldStatus === "idle" || oldStatus === "success")
              ) {
                  try {
                      // async write to clipboard
                      await navigator.clipboard.writeText(this.getCopyText());
                      this.copyStatus = "success";
                  } catch (err) {
                      console.log("Error copying to clipboard", err);
                      this.copyStatus = "idle";
                  }
              }
          },
      },

      // https://www.vuesnippets.com/posts/click-away/
      // https://dev.to/jamus/clicking-outside-the-box-making-your-vue-app-aware-of-events-outside-its-world-53nh
      directives: {
          clickaway: {
              bind(el, { value }) {
                  if (typeof value !== "function") {
                      console.warn(`Expect a function, got ${value}`);
                      return;
                  }

                  const clickawayHandler = (e) => {
                      const elementsOfInterest = Array.from(
                          el.parentElement.children
                      );
                      const clickedInside = elementsOfInterest.filter((el) =>
                          el.contains(e.target)
                      );
                      return clickedInside.length || value();
                  };

                  el.__clickawayEventHandler__ = clickawayHandler;

                  document.addEventListener("click", clickawayHandler);
              },
              unbind(el) {
                  document.removeEventListener(
                      "click",
                      el.__clickawayEventHandler__
                  );
              },
          },
      },

      methods: {
          handleEnter(e) {
              this.entered = !this.entered && !this.clicked;
              this.leftSafe = !leftWarning(e.currentTarget);
              this.anchorY = appendPxSuffix(
                  getAnchorY(e.currentTarget, this.btn_type)
              );
              this.anchorX = appendPxSuffix(getAnchorX(this.$el, this.btn_type));
          },
          handleExit() {
              if (!this.clicked) {
                  this.entered = false;
                  this.anchorY = undefined;
                  this.leftSafe = true;
              }
          },
          handleClick(e) {
              if (!this.clicked) {
                  this.entered = false;
                  this.clicked = true;
                  if (leftWarning(e.currentTarget)) {
                      this.leftSafe = false;
                  }
                  this.anchorY = appendPxSuffix(
                      getAnchorY(e.currentTarget, this.btn_type)
                  );
                  this.anchorX = appendPxSuffix(
                      getAnchorX(this.$el, this.btn_type)
                  );
              }
          },
          handleCloseClick() {
              if (this.clicked) {
                  this.clicked = false;
                  this.entered = false;
                  this.anchorY = undefined;
                  this.leftSafe = true;
                  this.selectedAction = null;
              }
          },
          handleActionClick(payload) {
              this.selectedAction = payload.actionType;
              this.copyStatus = "pending";
          },
          getCopyText() {
              return this.selectedAction === "citation"
                  ? this.formatted_citation
                  : `${new URL(window.location.href.split("#")[0]).toString()}#${
                      this.hash
                  }`;
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
    return _c("div", { staticClass: "copy-btn-container" }, [
      _c(
        "button",
        {
          staticClass: "copy-btn text-btn",
          class: _vm.buttonClasses,
          attrs: { "aria-label": _vm.ariaLabel },
          on: {
            focus: _vm.handleEnter,
            focusout: _vm.handleExit,
            mouseenter: _vm.handleEnter,
            mouseleave: _vm.handleExit,
            click: _vm.handleClick
          }
        },
        [
          _c("i", { staticClass: "fa fa-link" }),
          _vm._v(" "),
          _vm.btn_type === "labeled-icon"
            ? _c("span", [_vm._v(_vm._s(_vm.label))])
            : _vm._e()
        ]
      ),
      _vm._v(" "),
      _c(
        "div",
        {
          directives: [
            {
              name: "show",
              rawName: "v-show",
              value: _vm.entered && _vm.btn_type === "icon",
              expression: "entered && btn_type === 'icon'"
            }
          ],
          staticClass: "copy-tooltip hovered",
          class: _vm.tooltipClasses,
          style: _vm.tooltipStyles
        },
        [_c("p", { staticClass: "hover-msg" }, [_vm._v(_vm._s(_vm.label))])]
      ),
      _vm._v(" "),
      _vm.clicked
        ? _c(
            "div",
            {
              directives: [
                {
                  name: "clickaway",
                  rawName: "v-clickaway",
                  value: _vm.handleCloseClick,
                  expression: "handleCloseClick"
                }
              ],
              staticClass: "copy-tooltip clicked",
              class: _vm.tooltipClasses,
              style: _vm.tooltipStyles
            },
            [
              _c(
                "button",
                {
                  staticClass: "close-btn text-btn",
                  attrs: { "aria-label": "close copy link or citation dialog" },
                  on: { click: _vm.handleCloseClick }
                },
                [
                  _c(
                    "svg",
                    {
                      attrs: {
                        width: "11",
                        height: "11",
                        viewBox: "0 0 11 11",
                        fill: "none",
                        xmlns: "http://www.w3.org/2000/svg"
                      }
                    },
                    [
                      _c("path", {
                        attrs: {
                          "fill-rule": "evenodd",
                          "clip-rule": "evenodd",
                          d:
                            "M1.47149 1.08383L5.49969 5.11209L9.52851 1.08383C9.63637 0.975965 9.81124 0.975965 9.91911 1.08383C10.027 1.19169 10.027 1.36656 9.91911 1.47442L5.89023 5.50262L9.91911 9.53144C10.027 9.6393 10.027 9.81417 9.91911 9.92204C9.81124 10.0299 9.63637 10.0299 9.52851 9.92204L5.49969 5.89316L1.47149 9.92204C1.36363 10.0299 1.18876 10.0299 1.0809 9.92204C0.973035 9.81417 0.973035 9.6393 1.0809 9.53144L5.10916 5.50262L1.0809 1.47442C0.973035 1.36656 0.973035 1.19169 1.0809 1.08383C1.18876 0.975965 1.36363 0.975965 1.47149 1.08383Z"
                        }
                      })
                    ]
                  )
                ]
              ),
              _vm._v(" "),
              _c("p", { staticClass: "citation-title" }, [
                _vm._v(_vm._s(this.formatted_citation))
              ]),
              _vm._v(" "),
              _c(
                "div",
                { staticClass: "action-btns" },
                [
                  _c("ActionBtn", {
                    attrs: {
                      selectedAction: _vm.selectedAction,
                      status: _vm.copyStatus,
                      actionType: "link"
                    },
                    on: { "action-btn-click": _vm.handleActionClick }
                  }),
                  _vm._v(" "),
                  _c("ActionBtn", {
                    attrs: {
                      selectedAction: _vm.selectedAction,
                      status: _vm.copyStatus,
                      actionType: "citation"
                    },
                    on: { "action-btn-click": _vm.handleActionClick }
                  })
                ],
                1
              )
            ]
          )
        : _vm._e()
    ])
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
    

    
    const __vue_component__$2 = /*#__PURE__*/normalizeComponent$1(
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

  var script = {
      name: "table-component",

      props: {
          table_markup: {
              type: String,
              required: true,
          }

      },

      computed: {
          table() {
              return this.table_markup;
          }

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
  const __vue_script__ = script;

  /* template */
  var __vue_render__ = function() {
    var _vm = this;
    var _h = _vm.$createElement;
    var _c = _vm._self._c || _h;
    return _c("section", {
      staticClass: "table-section",
      domProps: { innerHTML: _vm._s(_vm.table) }
    })
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

  function goToVersion() {
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

  Vue__default['default'].config.devtools = true;

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
      new Vue__default['default']({
          components: {
              RelatedRules: __vue_component__$b,
              Collapsible: __vue_component__$a,
              CollapseButton: __vue_component__$9,
              SupplementalContent: __vue_component__$8,
              CopyBtn: __vue_component__$2,
              TableComponent: __vue_component__,
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

}(Vue));
//# sourceMappingURL=main.build.js.map
