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

    // -----------------------------------------------
    // Product Detail Page - Add to Cart / Wishlist AJAX
    // -----------------------------------------------
    const addToCartBtn = document.getElementById('addToCartBtn');
    const addToCartForm = document.getElementById('addToCartForm');
    
    if (addToCartBtn && addToCartForm) {
        addToCartBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const formData = new FormData(addToCartForm);
            
            // Get the current quantity from selector if it exists
            const qtyDisplay = document.querySelector('.qty-display');
            if (qtyDisplay) {
                formData.set('quantity', qtyDisplay.textContent.trim());
            }

            addToCartBtn.disabled = true;
            addToCartBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Adding...';

            fetch('/cart/add/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => res.json())
            .then(data => {
                addToCartBtn.disabled = false;
                addToCartBtn.innerHTML = '<i class="fa-solid fa-cart-plus"></i> Add to Cart';
                
                if (data.ok) {
                    showGlobalMessage(data.message, 'success');
                    updateBadgeCount('cart', data.cart_count);
                } else {
                    showGlobalMessage(data.message || 'Failed to add item to cart', 'error');
                }
            })
            .catch(err => {
                addToCartBtn.disabled = false;
                addToCartBtn.innerHTML = '<i class="fa-solid fa-cart-plus"></i> Add to Cart';
                showGlobalMessage('Network error occurred. Please try again.', 'error');
            });
        });
    }

    const wishlistToggleBtn = document.getElementById('wishlistToggleBtn');
    if (wishlistToggleBtn) {
        wishlistToggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Find CSRF token from cart form
            const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
            if (!csrfInput) {
                showGlobalMessage('Session error, please refresh the page.', 'error');
                return;
            }

            const productIdInput = document.querySelector('[name=product_id]');
            if (!productIdInput) return;

            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', csrfInput.value);
            formData.append('product_id', productIdInput.value);

            wishlistToggleBtn.disabled = true;
            wishlistToggleBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

            fetch('/wishlist/add/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(res => {
                if (res.status === 403 || res.redirected) {
                    // Not authenticated
                    window.location.href = '/auth/login/';
                    return;
                }
                return res.json();
            })
            .then(data => {
                if (!data) return;
                wishlistToggleBtn.disabled = false;
                
                if (data.ok) {
                    showGlobalMessage(data.message, 'success');
                    updateBadgeCount('wishlist', data.wishlist_count);
                    
                    // Update button styling
                    if (data.in_wishlist) {
                        wishlistToggleBtn.setAttribute('data-in-wishlist', 'true');
                        wishlistToggleBtn.style.color = 'var(--color-danger)';
                        wishlistToggleBtn.style.borderColor = 'var(--color-danger)';
                        wishlistToggleBtn.innerHTML = '<i class="fa-solid fa-heart"></i> In Wishlist';
                    } else {
                        wishlistToggleBtn.setAttribute('data-in-wishlist', 'false');
                        wishlistToggleBtn.style.color = '';
                        wishlistToggleBtn.style.borderColor = '';
                        wishlistToggleBtn.innerHTML = '<i class="fa-regular fa-heart"></i> Save Wishlist';
                    }
                } else {
                    showGlobalMessage(data.message || 'Failed to update wishlist', 'error');
                }
            })
            .catch(err => {
                wishlistToggleBtn.disabled = false;
                showGlobalMessage('Network error occurred. Please try again.', 'error');
            });
        });
    }

    // Helpers
    function showGlobalMessage(text, type) {
        const container = document.querySelector('.messages-container');
        if (!container) return;
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            <span>${text}</span>
            <i class="fa-solid fa-xmark close-btn" onclick="this.parentElement.remove()"></i>
        `;
        container.appendChild(alertDiv);
        
        // Auto remove
        setTimeout(() => {
            alertDiv.style.transition = 'opacity 0.5s ease';
            alertDiv.style.opacity = '0';
            setTimeout(() => alertDiv.remove(), 500);
        }, 5000);
    }

    function updateBadgeCount(type, count) {
        // Find badge in desktop nav
        const navItems = document.querySelectorAll('.nav-actions .nav-item');
        navItems.forEach(item => {
            const isCart = item.querySelector('.fa-cart-shopping') && type === 'cart';
            const isWishlist = item.querySelector('.fa-regular.fa-heart, .fa-solid.fa-heart') && type === 'wishlist';
            
            if (isCart || isWishlist) {
                let badge = item.querySelector('.badge');
                if (count > 0) {
                    if (!badge) {
                        badge = document.createElement('span');
                        badge.className = 'badge';
                        item.appendChild(badge);
                    }
                    badge.textContent = count;
                } else if (badge) {
                    badge.remove();
                }
            }
        });
        
        // Also update mobile bottom nav badges if present
        const bottomNavItems = document.querySelectorAll('.bottom-nav-item');
        bottomNavItems.forEach(item => {
            const isWishlist = item.querySelector('.fa-regular.fa-heart, .fa-solid.fa-heart') && type === 'wishlist';
            if (isWishlist) {
                let badge = item.querySelector('.badge');
                if (count > 0) {
                    if (!badge) {
                        badge = document.createElement('span');
                        badge.className = 'badge';
                        item.appendChild(badge);
                    }
                    badge.textContent = count;
                } else if (badge) {
                    badge.remove();
                }
            }
        });
    }
});
