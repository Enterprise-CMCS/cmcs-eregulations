import storage from '../../redux/storage';
import { activePane } from '../../redux/reducers';

const $ = require('jquery');
const Backbone = require('backbone');
const TOCView = require('./toc-view');
const HistoryView = require('./history-view');
const SearchView = require('./search-view');
const DrawerTabs = require('./drawer-tabs-view');

Backbone.$ = $;

const DrawerView = Backbone.View.extend({
  el: '#menu',

  events: {
    'click .section-subpart': 'toggleSection',
    'click .section-subjgrp': 'toggleSection',
  },

  toggleSection: function toggleSection(e) {
    const $target = $(e.currentTarget);
    const $sectionClass = `.${$target.attr('data-subgroup')}`;
    const $toggleEl = $('.toggle-toc-menu-sections').filter($sectionClass);

    e.preventDefault();
    $toggleEl.slideToggle(400);
  },

  initialize: function initialize(options) {
    storage().subscribe(this.handleReduxUpdate.bind(this));

    this.$label = $('.toc-type');
    this.$children = $('.toc-container');

    this.childViews = {};
    this.childViews['table-of-contents'] = new TOCView();
    this.childViews.timeline = new HistoryView();
    this.childViews.search = new SearchView();
    this.childViews['drawer-tabs'] = new DrawerTabs({ forceOpen: options.forceOpen });

    const $tocSecondary = $('#table-of-contents-secondary');
    if ($tocSecondary.length) {
      this.childViews['table-of-contents-secondary'] = new TOCView({ el: $tocSecondary });
    }

    this.setActivePane('table-of-contents');
    const $tocMenuSections = $('.toggle-toc-menu-sections');
    $tocMenuSections.hide();

    const url = location.hash;
    const nav_el = `#nav-${url.slice(1)}`;
    $(nav_el).parent().parent().show();
  },

    // page types are more diverse and are named differently for
    // semantic reasons, so we need to associate page types
    // with the drawer panes they should be associated with
  pageTypeMap: {
    diff: 'timeline',
    'reg-section': 'table-of-contents',
    error: 'table-of-contents',
    'search-results': 'search',
  },

  handleReduxUpdate: function handleReduxUpdate() {
    this.setActivePane(activePane(storage()));
  },

  // selectedId = page type or child view type
  setActivePane: function setActivePane(selectedId) {
    let activeId = selectedId;
    if (typeof this.childViews[activeId] === 'undefined') {
      activeId = this.pageTypeMap[activeId];
    }

    // hide the content of all drawer sections
    this.$children.addClass('hidden');

    // remove the 'hidden' class from the active drawer section
    this.childViews[activeId].$el.removeClass('hidden');
  },

});

module.exports = DrawerView;
