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
  name: 'supplementary-content-object',

  props: {
    title: {
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
const __vue_script__$6 = script$6;

/* template */
var __vue_render__$6 = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c("div", { staticClass: "supplementary-content" }, [
    _c(
      "a",
      {
        staticClass: "supplementary-content-link",
        attrs: { href: _vm.url, target: "_blank", rel: "noopener noreferrer" }
      },
      [
        _vm.date
          ? _c(
              "span",
              {
                staticClass: "supplementary-content-date",
                class: {
                  "supplementary-content-mid-bar": !_vm.isBlank(_vm.title)
                }
              },
              [_vm._v(_vm._s(_vm._f("formatDate")(_vm.date)))]
            )
          : _vm._e(),
        _vm._v(" "),
        !_vm.isBlank(_vm.title)
          ? _c(
              "span",
              {
                staticClass: "supplementary-content-title",
                class: {
                  "supplementary-content-external-link": _vm.isBlank(
                    _vm.description
                  )
                }
              },
              [_vm._v(_vm._s(_vm.title))]
            )
          : _vm._e(),
        _vm._v(" "),
        !_vm.isBlank(_vm.description)
          ? _c(
              "div",
              {
                staticClass:
                  "supplementary-content-description supplementary-content-external-link"
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
  

  
  const __vue_component__$6 = /*#__PURE__*/normalizeComponent(
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
const __vue_script__$5 = script$5;

/* template */
var __vue_render__$5 = function() {
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

var script$4 = {
    name: 'supplementary-content-list',

    components: {
        SupplementaryContentObject: __vue_component__$6,
        ShowMoreButton: __vue_component__$5,
    },

    props: {
        supplementary_content: {
            type: Array,
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
            limitedList: true,
        }
    },

    computed: {
        limitedContent() {
            if(this.limitedList) {
                return this.supplementary_content.slice(0, this.limit);
            }
            return this.supplementary_content;
        },
        contentCount() {
            return this.supplementary_content.length;
        },
        showMoreNeeded() {
            return this.contentCount > this.limit;
        },
    },

    methods: {
        showMore() {
            this.limitedList = !this.limitedList;
        }
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
    "div",
    { staticClass: "supplementary-content-list" },
    [
      _vm._l(_vm.limitedContent, function(content, index) {
        return _c("supplementary-content-object", {
          key: index,
          attrs: {
            title: content.title,
            description: content.description,
            date: content.date,
            url: content.url
          }
        })
      }),
      _vm._v(" "),
      _vm.showMoreNeeded
        ? _c("show-more-button", {
            attrs: { showMore: _vm.showMore, count: _vm.contentCount }
          })
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

var script$3 = {
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
const __vue_script__$3 = script$3;

/* template */
var __vue_render__$3 = function() {
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

var script$1 = {
    name: 'supplementary-content-category',

    components: {
        SupplementaryContentList: __vue_component__$4,
        CollapseButton: __vue_component__$3,
        Collapsible: __vue_component__$2,
    },

    props: {
        subcategory: {
            type: Boolean,
            required: false,
            default: false,
        },
        title: {
            type: String,
            required: true,
        },
        description: {
            type: String,
            required: true,
        },
        supplementary_content: {
            type: Array,
            required: false,
        },
        sub_categories: {
            type: Array,
            required: false,
        },
    },

    computed: {
        showDescription: function() {
            return (this.description && !/^\s*$/.test(this.description));
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
  return _c("div", { staticClass: "supplementary-content-category" }, [
    _c(
      "div",
      { staticClass: "category-toggle-container" },
      [
        _c("collapse-button", {
          staticClass: "category-toggle",
          attrs: { name: _vm.title, state: "collapsed" },
          scopedSlots: _vm._u([
            {
              key: "expanded",
              fn: function() {
                return [_c("i", { staticClass: "fa fa-chevron-up" })]
              },
              proxy: true
            },
            {
              key: "collapsed",
              fn: function() {
                return [_c("i", { staticClass: "fa fa-chevron-down" })]
              },
              proxy: true
            }
          ])
        })
      ],
      1
    ),
    _vm._v(" "),
    _c(
      "div",
      { staticClass: "category" },
      [
        _c("collapse-button", {
          staticClass: "category-title",
          class: { subcategory: _vm.subcategory },
          attrs: { name: _vm.title, state: "collapsed" },
          scopedSlots: _vm._u([
            {
              key: "expanded",
              fn: function() {
                return [_vm._v(_vm._s(_vm.title))]
              },
              proxy: true
            },
            {
              key: "collapsed",
              fn: function() {
                return [_vm._v(_vm._s(_vm.title))]
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
            attrs: { name: _vm.title, state: "collapsed" }
          },
          [
            _vm._l(_vm.sub_categories, function(category, index) {
              return _c("supplementary-content-category", {
                key: index,
                attrs: {
                  subcategory: true,
                  title: category.title,
                  description: category.description,
                  supplementary_content: category.supplementary_content,
                  sub_categories: category.sub_categories
                }
              })
            }),
            _vm._v(" "),
            _c("supplementary-content-list", {
              attrs: { supplementary_content: _vm.supplementary_content }
            })
          ],
          2
        )
      ],
      1
    )
  ])
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
        SupplementaryContentCategory: __vue_component__$1,
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
            required: true,
        },
    },

    data() {
        return {
            categories: [],
        }
    },

    async created() {
        this.categories = await this.fetch_content(this.title, this.part, this.sections);
    },

    methods: {
        async fetch_content(title, part, sections) {
            const joinedSections = sections.join("&sections=");
            const response = await fetch(`${this.api_url}title/${title}/part/${part}/supplementary_content?&sections=${joinedSections}`);
            const content = await response.json();
            return content;
        },
    }
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
    { staticClass: "supplementary-content-container" },
    _vm._l(_vm.categories, function(category, index) {
      return _c("supplementary-content-category", {
        key: index,
        attrs: {
          title: category.title,
          description: category.description,
          supplementary_content: category.supplementary_content,
          sub_categories: category.sub_categories
        }
      })
    }),
    1
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
//# sourceMappingURL=SupplementaryContent.js.map
