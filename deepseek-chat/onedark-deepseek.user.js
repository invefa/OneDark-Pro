// ==UserScript==
// @name         One Dark Pro Darker for DeepSeek Chat
// @namespace    local.onedarkpro.deepseek
// @version      1.0.0
// @description  Apply the One Dark Pro Darker palette to chat.deepseek.com by remapping its design tokens.
// @match        https://chat.deepseek.com/*
// @run-at       document-start
// @grant        none
// ==/UserScript==

(function () {
  "use strict";

  var CONFIG = {
    // set to false to switch the whole skin off
    enabled: true,
    // these tokens only exist in dark mode; switch the site to dark first
    requireDarkAttribute: true
  };

  if (!CONFIG.enabled) return;

  var CSS = String.raw`/* One Dark Pro Darker for chat.deepseek.com
   Palette extracted from VSCode theme zhuangtongfa.material-theme 3.20.3.
   Applied to DeepSeek's own design tokens, so newly rendered parts follow too. */

body[data-ds-dark-theme] {
  /* raw palette: neutral ramp */
  --dsw-static-neutral-bluish-00: #ffffff !important;
  --dsw-static-neutral-bluish-50: #abb2bf !important;
  --dsw-static-neutral-bluish-60: #abb2bf !important;
  --dsw-static-neutral-bluish-75: #9da5b4 !important;
  --dsw-static-neutral-bluish-100: #9da5b4 !important;
  --dsw-static-neutral-bluish-150: #9da5b4 !important;
  --dsw-static-neutral-bluish-200: #9da5b4 !important;
  --dsw-static-neutral-bluish-300: #9da5b4 !important;
  --dsw-static-neutral-bluish-400: #7f848e !important;
  --dsw-static-neutral-bluish-500: #7f848e !important;
  --dsw-static-neutral-bluish-600: #6b717d !important;
  --dsw-static-neutral-bluish-700: #495162 !important;
  --dsw-static-neutral-bluish-750: #3e4452 !important;
  --dsw-static-neutral-bluish-800: #323842 !important;
  --dsw-static-neutral-bluish-850: #2c313c !important;
  --dsw-static-neutral-bluish-875: #2c313a !important;
  --dsw-static-neutral-bluish-900: #1e2227 !important;
  --dsw-static-neutral-bluish-950: #23272e !important;
  --dsw-static-neutral-bluish-1000: #181a1f !important;

  /* raw palette: brand blues */
  --dsw-static-deepseek-50: #23272e !important;
  --dsw-static-deepseek-100: #2c313c !important;
  --dsw-static-deepseek-200: #323842 !important;
  --dsw-static-deepseek-300: #3e4452 !important;
  --dsw-static-deepseek-400: #61afef !important;
  --dsw-static-deepseek-450: #528bff !important;
  --dsw-static-deepseek-500: #4d78cc !important;
  --dsw-static-deepseek-600: #528bff !important;
  --dsw-static-deepseek-700: #4d78cc !important;
  --dsw-static-deepseek-700-delete: #4d78cc !important;
  --dsw-static-deepseek-800: #2c313c !important;
  --dsw-static-deepseek-900: #2c313c !important;

  /* raw palette: status hues */
  --dsw-static-red-400: #e06c75 !important;
  --dsw-static-red-500: #e06c75 !important;
  --dsw-static-red-600: #c24038 !important;
  --dsw-static-red-900: rgba(224, 108, 117, .15) !important;
  --dsw-static-green-400: #98c379 !important;
  --dsw-static-green-500: #98c379 !important;
  --dsw-static-green-900: rgba(152, 195, 121, .15) !important;
  --dsw-static-amber-400: #d19a66 !important;
  --dsw-static-amber-500: #d19a66 !important;
  --dsw-static-amber-600: #d19a66 !important;
  --dsw-static-amber-900: rgba(209, 154, 102, .15) !important;
  --dsw-static-blue-400: #61afef !important;
  --dsw-static-blue-450: #528bff !important;
  --dsw-static-blue-500: #4d78cc !important;
  --dsw-static-blue-600: #528bff !important;
  --dsw-static-blue-800: #2c313c !important;
  --dsw-static-blue-950: #23272e !important;

  /* semantic layer */
  --dsw-alias-bg-base: #23272e !important;
  --dsw-alias-bg-layer-1: #2c313c !important;
  --dsw-alias-bg-layer-2: #323842 !important;
  --dsw-alias-bg-layer-3: #3e4452 !important;
  --dsw-alias-bg-overlay: #323842 !important;
  --dsw-alias-bg-multi-select: #323842 !important;
  --dsw-alias-bg-module-platform: #323842 !important;
  --dsw-alias-bg-skeleton: #2c313a !important;
  --dsw-alias-border-l1: #2c313c !important;
  --dsw-alias-border-l2: #3e4452 !important;
  --dsw-alias-border-l2-darkmode-thin: #2c313c !important;
  --dsw-alias-border-l3: #495162 !important;
  --dsw-alias-border-l4: #515a6b !important;
  --dsw-alias-border-inverted: #2c313c !important;
  --dsw-alias-border-inverted2: #3e4452 !important;
  --dsw-alias-interactive-bg-hover: #2c313a !important;
  --dsw-alias-interactive-bg-hover-accent: #323842 !important;
  --dsw-alias-interactive-bg-active: #2c313c !important;
  --dsw-alias-interactive-bg-hover-danger: rgba(224, 108, 117, .15) !important;
  --dsw-alias-interactive-bg-hover-solid: #2c313a !important;
  --dsw-alias-brand-primary: #4d78cc !important;
  --dsw-alias-brand-primary-invert: #ffffff !important;
  --dsw-alias-brand-text: #61afef !important;
  --dsw-alias-button-primary-fill: #4d78cc !important;
  --dsw-alias-button-primary-hover: #528bff !important;
  --dsw-alias-button-primary-dimmed: #323842 !important;
  --dsw-alias-button-info-fill: #4d78cc !important;
  --dsw-alias-button-info-hover: #528bff !important;
  --dsw-alias-button-elevated-fill: #323842 !important;
  --dsw-alias-button-floating-fill: #323842 !important;
  --dsw-alias-button-floating-hover: #3e4452 !important;
  --dsw-alias-button-ghost-active-fill: #2c313c !important;
  --dsw-alias-button-ghost-active-hover: #323842 !important;
  --dsw-alias-button-ghost-active-border: #4d78cc !important;
  --dsw-alias-button-tool-bar-fill: rgba(44, 49, 58, .6) !important;
  --dsw-alias-button-tool-bar-hover: rgba(44, 49, 58, .8) !important;
  --dsw-alias-button-tool-bar-fill-invisible: rgba(24, 26, 31, .36) !important;
  --dsw-alias-button-contrast-fill: #abb2bf !important;
  --dsw-alias-label-primary: #abb2bf !important;
  --dsw-alias-label-primary-dimmed: #9da5b4 !important;
  --dsw-alias-label-secondary: #abb2bf !important;
  --dsw-alias-label-tertiary: #abb2bf !important;
  --dsw-alias-label-caption: #9da5b4 !important;
  --dsw-alias-label-dimmed: #495162 !important;
  --dsw-alias-label-primary-foreground: #ffffff !important;
  --dsw-alias-label-primary-inverted: #23272e !important;
  --dsw-alias-markdown-code-block: #1e2227 !important;
  --dsw-alias-markdown-code-block-banner: #23272e !important;
  --dsw-alias-markdown-inline-code: #2c313c !important;
  --dsw-alias-markdown-citation: #2c313c !important;
  --dsw-alias-markdown-tag: #2c313c !important;
  --dsw-alias-markdown-placeholder: #2c313c !important;
  --dsw-alias-markdown-code-segment-selected: #323842 !important;
  --dsw-alias-markdown-code-segment-unselected: #2c313c !important;
  --dsw-alias-scrollbar-bg-l1: #3e4452 !important;
  --dsw-alias-scrollbar-bg-l2: #495162 !important;
  --dsw-alias-scrollbar-hover-l1: #495162 !important;
  --dsw-alias-scrollbar-hover-l2: #515a6b !important;
  --dsw-alias-toast-bg: #323842 !important;
  --dsw-alias-tooltip-bg: #323842 !important;
  --dsw-specific-bubble: #2c313a !important;
  --dsw-specific-bubble-highlight: #323842 !important;
  --dsw-specific-input-major: #1d1f23 !important;
  --dsw-specific-login-input: #1e2227 !important;
  --dsw-specific-menu: #323842 !important;
  --dsw-specific-selector: #2c313c !important;
  --dsw-specific-sidebar-fill: #1e2227 !important;
  --dsw-specific-sidebar-nav-item-hover: #2c313a !important;
  --dsw-specific-sidebar-nav-item-active: #323842 !important;
  --dsw-specific-sidebar-nav-item-active-accent: #3e4452 !important;
  --dsw-linear-gradient-think: linear-gradient(180deg, #23272e 20.19%, rgba(35, 39, 46, 0) 100%) !important;
  --scroll-color: rgba(78, 86, 102, .6) !important;
  --dsl-a-text-color: #61afef !important;
  --dsl-a-text-hover-color: #528bff !important;
}

/* thinking block: a process column under the answer
   The site already ships the icon, the left rule and the 22px indent, but it colours
   reasoning with label-secondary, which in this mapping is the body colour, so the block
   needs its own step down. */
body[data-ds-dark-theme] .ds-think-content .ds-markdown {
  color: #7f848e;
  line-height: 22px;
}

body[data-ds-dark-theme] .ds-think-content .ds-markdown :is(h1, h2, h3, h4, h5, h6) {
  color: #9da5b4;
}

body[data-ds-dark-theme] .ds-think-content .ds-markdown :is(strong, b) {
  color: #abb2bf;
}

body[data-ds-dark-theme] .ds-think-content .ds-markdown :is(p, .ds-markdown-paragraph) {
  margin: 8px 0;
}

/* code block syntax */
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.comment,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.prolog,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.doctype,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.cdata,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-markdown .token.hr.punctuation,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-markdown .token.blockquote.punctuation {
  color: #7f848e;
}

body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.punctuation,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.parameter,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-markdown .token.table-header,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-json .token.operator {
  color: #abb2bf;
}

body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.tag,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.tag .token.punctuation,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.deleted,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.important,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.delimiter.important,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.selector,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.selector .parent,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.property,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.property-access,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.variable,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.key,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.regex,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.keyword-this,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.this,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-scss .token.variable,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-markdown .token.list.punctuation {
  color: #e06c75;
}

body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.class-name {
  color: #e5c07b;
}

body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.keyword,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.operator,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.atrule .token.rule,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.combinator,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.pseudo-class,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.pseudo-element {
  color: #c678dd;
}

body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.function,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.selector .token.class,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.selector .token.id,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-markdown .token.title,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-markdown .token.title .token.punctuation,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-markdown .token.url .token.content,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-markdown .token.url-link {
  color: #61afef;
}

body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.builtin,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.keyword-array,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.package {
  color: #56b6c2;
}

body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.string,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.attr-value,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.inserted,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.color,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.selector .value,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.string .token.url-link,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .language-markdown .token.code {
  color: #98c379;
}

body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.attr-name,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.boolean,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.boolean.important,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.number,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.constant,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.selector .attribute,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .token.unit {
  color: #d19a66;
}

/* code block base text and background */
body[data-ds-dark-theme] .md-code-block.md-code-block-dark code[class*=language-],
body[data-ds-dark-theme] .md-code-block.md-code-block-dark pre[class*=language-] {
  color: #abb2bf;
  background: none;
}

body[data-ds-dark-theme].md-code-block {
  background: #1e2227;
  border-color: #3e4452;
}

/* rainbow brackets and line numbers */
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-1 {
  color: #d19a66;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-2 {
  color: #c678dd;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-3 {
  color: #56b6c2;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-4 {
  color: #e5c07b;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-5 {
  color: #d19a66;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-6 {
  color: #c678dd;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-7 {
  color: #56b6c2;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-8 {
  color: #e5c07b;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-9 {
  color: #d19a66;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-10 {
  color: #c678dd;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-11 {
  color: #56b6c2;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .rainbow-braces .token.token.punctuation.brace-level-12 {
  color: #e5c07b;
}

body[data-ds-dark-theme] .md-code-block.md-code-block-dark .line-numbers-rows > span:before {
  color: #495162;
}
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .line-highlight,
body[data-ds-dark-theme] .md-code-block.md-code-block-dark .line-highlight:before {
  background: #2c313c;
}

/* selection */
body[data-ds-dark-theme] ::selection {
  background: #3d4555;
}
`;

  function inject() {
    if (document.getElementById("onedark-pro-darker")) return;
    if (CONFIG.requireDarkAttribute && !document.body.hasAttribute("data-ds-dark-theme")) {
      // in light mode leave the page alone and wait for the dark theme attribute
      var wait = new MutationObserver(function () {
        if (document.body.hasAttribute("data-ds-dark-theme")) {
          wait.disconnect();
          inject();
        }
      });
      wait.observe(document.body, { attributes: true, attributeFilter: ["data-ds-dark-theme"] });
      return;
    }
    var style = document.createElement("style");
    style.id = "onedark-pro-darker";
    style.textContent = CSS;
    document.head.appendChild(style);
    console.log("[One Dark Pro Darker] skin injected");
  }

  function start() {
    if (document.body) {
      inject();
    } else {
      document.addEventListener("DOMContentLoaded", inject, { once: true });
    }
  }

  start();
})();
