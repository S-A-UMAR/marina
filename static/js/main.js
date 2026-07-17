/* ============================================================
   MARINA GLOBAL JAVASCRIPT UTILITIES
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {

    // -----------------------------------------------
    // SIDEBAR DRAWER
    // -----------------------------------------------
    const openBtn    = document.getElementById('sidebarOpen');
    const closeBtn   = document.getElementById('sidebarClose');
    const drawer     = document.getElementById('sidebarDrawer');
    const overlay    = document.getElementById('sidebarOverlay');

    function openSidebar() {
        if (drawer) drawer.classList.add('open');
        if (overlay) overlay.classList.add('active');
        document.body.classList.add('sidebar-open');
        if (closeBtn) closeBtn.focus();
    }

    function closeSidebar() {
        if (drawer) drawer.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
        document.body.classList.remove('sidebar-open');
        if (openBtn) openBtn.focus();
    }

    if (openBtn)  openBtn.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    if (overlay)  overlay.addEventListener('click', closeSidebar);

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && drawer && drawer.classList.contains('open')) {
            closeSidebar();
        }
    });

    // Swipe-left to close on touch devices
    let touchStartX = 0;
    if (drawer) {
        drawer.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        drawer.addEventListener('touchend', (e) => {
            const deltaX = e.changedTouches[0].screenX - touchStartX;
            if (deltaX < -60) closeSidebar(); // swipe left ≥ 60px
        }, { passive: true });
    }

    // -----------------------------------------------
    // Auto-dismiss alerts/messages after 5 seconds
    // -----------------------------------------------
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // -----------------------------------------------
    // Product Detail Page - Thumbnail Image Switcher
    // -----------------------------------------------
    const thumbnails = document.querySelectorAll('.gallery-thumb');
    const mainImg = document.querySelector('.gallery-main img');

    if (thumbnails.length > 0 && mainImg) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                const imgEl = this.querySelector('img');
                if (imgEl) mainImg.src = imgEl.src;
            });
        });
    }

    // -----------------------------------------------
    // Product Detail Page - Tabs Switcher
    // -----------------------------------------------
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    if (tabBtns.length > 0) {
        tabBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const targetTab = this.getAttribute('data-tab');
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));

                this.classList.add('active');
                const targetContent = document.getElementById(targetTab);
                if (targetContent) targetContent.classList.add('active');
            });
        });
    }

    // -----------------------------------------------
    // Product Detail Page - Quantity Selector +/- Buttons
    // -----------------------------------------------
    const qtyDisplay = document.querySelector('.qty-display');
    const plusBtn  = document.querySelector('.qty-btn-plus');
    const minusBtn = document.querySelector('.qty-btn-minus');
    const hiddenQtyInput = document.getElementById('hiddenQuantity');

    if (qtyDisplay && hiddenQtyInput) {
        const max = parseInt(qtyDisplay.getAttribute('data-max')) || 999;
        
        if (plusBtn) {
            plusBtn.addEventListener('click', () => {
                let current = parseInt(qtyDisplay.textContent) || 1;
                if (current < max) {
                    current += 1;
                    qtyDisplay.textContent = current;
                    hiddenQtyInput.value = current;
                }
            });
        }
        if (minusBtn) {
            minusBtn.addEventListener('click', () => {
                let current = parseInt(qtyDisplay.textContent) || 1;
                if (current > 1) {
                    current -= 1;
                    qtyDisplay.textContent = current;
                    hiddenQtyInput.value = current;
                }
            });
        }
    }
});
