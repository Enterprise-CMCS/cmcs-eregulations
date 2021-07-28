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

var script = {
    name: "collapsible",

    created: function () {
        requestAnimationFrame(() => {
            this.visible = this.state === "expanded";
            this.isVertical = this.direction === "vertical";
        });
        this.$root.$on("collapse-toggle", this.toggle);
    },

    mounted: function () {
        window.addEventListener("resize", this.resize);
    },

    destroyed: function () {
        window.removeEventListener("resize", this.resize);
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
            default: "1s",
        },
        direction: {
            //horizontal or vertical
            type: String,
            required: true,
        },
    },

    data: function () {
        return {
            size: "auto",
            visible: false,
            isVertical: true,
            styles: {
                overflow: "hidden",
                transition: this.transition,
            },
        };
    },

    computed: {
        sizeStyle: function () {
            return this.isVertical
                ? { height: this.size }
                : { width: this.size };
        },
    },

    methods: {
        resize: function (e) {
            this.computeSize();
        },
        toggle: function (target) {
            if (this.name === target) {
                requestAnimationFrame(() => {
                    this.computeSize();
                    requestAnimationFrame(() => {
                        this.visible = !this.visible;
                    });
                });
            }
        },
        getStyle: function () {
            return window.getComputedStyle(this.$refs.target);
        },
        setProps: function (visibility, display, position, size) {
            this.$refs.target.style.visibility = visibility;
            this.$refs.target.style.display = display;
            this.$refs.target.style.position = position;
            if (this.isVertical) {
                this.$refs.target.style.height = size;
            } else {
                this.$refs.target.style.width = size;
            }
        },
        _computeSize: function() {
            if (this.getStyle().display === "none") {
                return "auto";
            }

            this.$refs.target.classList.remove("invisible");
            
            this.setProps("hidden", "block", "absolute", "auto");

            const size = this.isVertical
                ? this.getStyle().height
                : this.getStyle().width;

            this.setProps(null, null, null, size);
            if (!this.visible) {
                this.$refs.target.classList.add("invisible");
            }
            return size;
        },
        computeSize: function () {
            this.size = this._computeSize();
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
const __vue_script__ = script;

/* template */
var __vue_render__ = function() {
  var _vm = this;
  var _h = _vm.$createElement;
  var _c = _vm._self._c || _h;
  return _c(
    "div",
    {
      ref: "target",
      class: { invisible: !_vm.visible },
      style: [_vm.styles, _vm.sizeStyle]
    },
    [_vm._t("default")],
    2
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
