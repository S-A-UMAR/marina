/* ================================================================
   MARINA STAFF DASHBOARD — dashboard.js
   Handles: sidebar toggle, AJAX cart/wishlist, delete confirms
   ================================================================ */
(function () {
  'use strict';

  /* ---------------------------------------------------------------
     SIDEBAR DRAWER (mobile)
  --------------------------------------------------------------- */
  const hamburger  = document.getElementById('staffHamburger');
  const closeBtn   = document.getElementById('staffSidebarClose');
  const sidebar    = document.getElementById('staffSidebar');
  const overlay    = document.getElementById('staffOverlay');

  function openSidebar() {
    if (!sidebar) return;
    sidebar.classList.add('is-open');
    if (overlay) overlay.classList.add('is-open');
    document.body.classList.add('sidebar-lock');
    if (hamburger) hamburger.setAttribute('aria-expanded', 'true');
    if (closeBtn) closeBtn.focus();
  }

  function closeSidebar() {
    if (!sidebar) return;
    sidebar.classList.remove('is-open');
    if (overlay) overlay.classList.remove('is-open');
    document.body.classList.remove('sidebar-lock');
    if (hamburger) {
      hamburger.setAttribute('aria-expanded', 'false');
      hamburger.focus();
    }
  }

  if (hamburger) hamburger.addEventListener('click', openSidebar);
  if (closeBtn)  closeBtn.addEventListener('click', closeSidebar);
  if (overlay)   overlay.addEventListener('click', closeSidebar);

  // Escape key closes sidebar
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar && sidebar.classList.contains('is-open')) {
      closeSidebar();
    }
  });

  // Swipe-left gesture to close
  var touchStartX = 0;
  if (sidebar) {
    sidebar.addEventListener('touchstart', function (e) {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    sidebar.addEventListener('touchend', function (e) {
      if (e.changedTouches[0].screenX - touchStartX < -60) closeSidebar();
    }, { passive: true });
  }

  /* ---------------------------------------------------------------
     CONFIRM DELETE — add data-confirm="Your message" to any link
     or form to show a native confirm dialog before submitting.
  --------------------------------------------------------------- */
  document.querySelectorAll('[data-confirm]').forEach(function (el) {
    el.addEventListener('click', function (e) {
      if (!confirm(el.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

  /* ---------------------------------------------------------------
     AUTO-DISMISS DASHBOARD ALERTS after 6 s
  --------------------------------------------------------------- */
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(function () { if (alert.parentNode) alert.remove(); }, 500);
    }, 6000);
  });

})();
