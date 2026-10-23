/**
 * Lightweight background-image loader.
 *
 * - data-bg: load when the element approaches the viewport.
 * - data-bg-deferred: load after the page's load event (used for non-first
 *   hero slides, so the first screen is not competing with them).
 *
 * No timers, no artificial bandwidth limits: the browser decides priority.
 */
(function () {
  'use strict';

  function setBackground(element, attribute) {
    var source = element.getAttribute(attribute);
    if (!source) {
      return;
    }
    element.style.backgroundImage = 'url("' + source.replace(/"/g, '\\"') + '")';
    element.removeAttribute(attribute);
  }

  var lazyElements = document.querySelectorAll('[data-bg]');
  var deferredElements = document.querySelectorAll('[data-bg-deferred]');

  if (!lazyElements.length && !deferredElements.length) {
    return;
  }

  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          setBackground(entry.target, 'data-bg');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '200px 0px' });

    Array.prototype.forEach.call(lazyElements, function (element) {
      observer.observe(element);
    });
  } else {
    Array.prototype.forEach.call(lazyElements, function (element) {
      setBackground(element, 'data-bg');
    });
  }

  function loadDeferred() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-bg-deferred]'), function (element) {
      setBackground(element, 'data-bg-deferred');
    });
  }

  if (document.readyState === 'complete') {
    loadDeferred();
  } else {
    window.addEventListener('load', loadDeferred);
  }
})();
