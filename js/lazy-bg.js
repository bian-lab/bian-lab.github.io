/**
 * Lightweight background-image loader.
 *
 * Elements marked with data-bg are loaded when they approach the viewport.
 * Above-the-fold headers are started on the next animation frame, so the page
 * text can paint first without waiting for the image. No timers and no
 * artificial bandwidth limits: the browser decides the actual priority.
 */
(function () {
  'use strict';

  function setBackground(element) {
    var source = element.getAttribute('data-bg');
    if (!source) {
      return;
    }
    element.style.backgroundImage = 'url("' + source.replace(/"/g, '\\"') + '")';
    element.removeAttribute('data-bg');
  }

  function isNearViewport(element) {
    var rect = element.getBoundingClientRect();
    return rect.top < window.innerHeight + 200 && rect.bottom > -200;
  }

  var lazyElements = Array.prototype.slice.call(document.querySelectorAll('[data-bg]'));
  if (!lazyElements.length) {
    return;
  }

  var nearElements = [];
  var farElements = [];

  lazyElements.forEach(function (element) {
    if (isNearViewport(element)) {
      nearElements.push(element);
    } else {
      farElements.push(element);
    }
  });

  function loadNearElements() {
    nearElements.forEach(setBackground);
  }

  if (window.requestAnimationFrame) {
    window.requestAnimationFrame(loadNearElements);
  } else {
    loadNearElements();
  }

  if (!farElements.length) {
    return;
  }

  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          setBackground(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '200px 0px' });

    farElements.forEach(function (element) {
      observer.observe(element);
    });
  } else {
    farElements.forEach(setBackground);
  }
})();
