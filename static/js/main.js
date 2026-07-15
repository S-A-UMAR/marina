/* HUMJID Global Storefront JS Utilities */
document.addEventListener('DOMContentLoaded', () => {

    // -----------------------------------------------
    // SIDEBAR DRAWER
    // -----------------------------------------------
    const openBtn    = document.getElementById('sidebarOpen');
    const closeBtn   = document.getElementById('sidebarClose');
    const drawer     = document.getElementById('sidebarDrawer');
    const overlay    = document.getElementById('sidebarOverlay');

    function openSidebar() {
        drawer.classList.add('active');
        overlay.classList.add('active');
        document.body.classList.add('sidebar-open');
        if (closeBtn) closeBtn.focus();
    }

    function closeSidebar() {
        drawer.classList.remove('active');
        overlay.classList.remove('active');
        document.body.classList.remove('sidebar-open');
        if (openBtn) openBtn.focus();
    }

    if (openBtn)  openBtn.addEventListener('click', openSidebar);
    if (closeBtn) closeBtn.addEventListener('click', closeSidebar);
    if (overlay)  overlay.addEventListener('click', closeSidebar);

    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && drawer && drawer.classList.contains('active')) {
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
    // Auto-dismiss alert messages after 5 seconds
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
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImg = document.querySelector('.main-image img');

    if (thumbnails.length > 0 && mainImg) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                thumbnails.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                const newSrc = this.querySelector('img').src;
                mainImg.src = newSrc;
            });
        });
    }

    // -----------------------------------------------
    // Product Detail Page - Quantity Selector +/- Buttons
    // -----------------------------------------------
    const qtyInput = document.querySelector('.qty-input input');
    const plusBtn  = document.querySelector('.qty-input .plus');
    const minusBtn = document.querySelector('.qty-input .minus');

    if (qtyInput) {
        if (plusBtn) {
            plusBtn.addEventListener('click', () => {
                const max = parseInt(qtyInput.getAttribute('max')) || 999;
                let current = parseInt(qtyInput.value) || 1;
                if (current < max) qtyInput.value = current + 1;
            });
        }
        if (minusBtn) {
            minusBtn.addEventListener('click', () => {
                let current = parseInt(qtyInput.value) || 1;
                if (current > 1) qtyInput.value = current - 1;
            });
        }
    }

});

