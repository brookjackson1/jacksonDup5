/**
 * Delta Airlines Employee Portal - Main JavaScript
 * Enhanced functionality and interactivity
 */

// ================================================
// Table Search Functionality
// ================================================

/**
 * Initialize table search functionality
 * @param {string} searchInputId - ID of the search input
 * @param {string} tableId - ID of the table to search
 */
function initTableSearch(searchInputId, tableId) {
    const searchInput = document.getElementById(searchInputId);
    const table = document.getElementById(tableId);

    if (!searchInput || !table) return;

    searchInput.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const tbody = table.querySelector('tbody');
        const rows = tbody.getElementsByTagName('tr');

        let visibleCount = 0;

        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let found = false;

            for (let j = 0; j < cells.length; j++) {
                const cellText = cells[j].textContent || cells[j].innerText;
                if (cellText.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }

            if (found) {
                row.style.display = '';
                visibleCount++;

                // Add fade-in animation
                row.style.animation = 'fadeIn 0.3s ease';
            } else {
                row.style.display = 'none';
            }
        }

        // Show/hide "no results" message
        showNoResults(tbody, visibleCount, filter);
    });
}

/**
 * Show "no results" message when table is empty
 */
function showNoResults(tbody, visibleCount, searchTerm) {
    let noResultsRow = tbody.querySelector('.no-results-row');

    if (visibleCount === 0 && searchTerm !== '') {
        if (!noResultsRow) {
            const colCount = tbody.querySelector('tr')?.getElementsByTagName('td').length || 1;
            noResultsRow = document.createElement('tr');
            noResultsRow.className = 'no-results-row';
            noResultsRow.innerHTML = `
                <td colspan="${colCount}" class="text-center py-4">
                    <div class="empty-state">
                        <i class="fas fa-search fa-3x mb-3 d-block" style="color: var(--delta-blue); opacity: 0.3;"></i>
                        <h5>No results found</h5>
                        <p class="text-muted">Try adjusting your search terms</p>
                    </div>
                </td>
            `;
            tbody.appendChild(noResultsRow);
        }
        noResultsRow.style.display = '';
    } else if (noResultsRow) {
        noResultsRow.style.display = 'none';
    }
}

// ================================================
// Form Validation
// ================================================

/**
 * Add real-time form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');

    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();

                // Add shake animation to invalid fields
                const invalidFields = form.querySelectorAll(':invalid');
                invalidFields.forEach(field => {
                    field.classList.add('shake');
                    setTimeout(() => field.classList.remove('shake'), 500);
                });
            }

            form.classList.add('was-validated');
        }, false);
    });
}

// ================================================
// Loading Overlay
// ================================================

/**
 * Show loading overlay
 */
function showLoading() {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary mb-3" role="status" style="width: 3rem; height: 3rem;">
                <span class="visually-hidden">Loading...</span>
            </div>
            <h5 style="color: var(--delta-blue);">Loading...</h5>
        </div>
    `;
    document.body.appendChild(overlay);
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// ================================================
// Toast Notifications
// ================================================

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of notification (success, danger, warning, info)
 */
function showToast(message, type = 'info') {
    const toastContainer = getOrCreateToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();

    // Remove toast from DOM after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Get or create toast container
 */
function getOrCreateToastContainer() {
    let container = document.getElementById('toastContainer');

    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }

    return container;
}

// ================================================
// Confirm Delete Dialog
// ================================================

/**
 * Enhanced confirm delete with better UX
 */
function confirmDeleteAction(itemName, actionUrl) {
    if (confirm(`Are you sure you want to archive ${itemName}?\n\nThis item will be moved to the archive and can be restored later.`)) {
        showLoading();
        window.location.href = actionUrl;
    }
}

// ================================================
// Table Row Highlighting
// ================================================

/**
 * Add click-to-highlight functionality to table rows
 */
function initTableRowHighlight() {
    const tables = document.querySelectorAll('.table');

    tables.forEach(table => {
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            row.addEventListener('click', function(e) {
                // Don't highlight if clicking on a button or link
                if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' ||
                    e.target.closest('button') || e.target.closest('a')) {
                    return;
                }

                // Remove previous highlight
                rows.forEach(r => r.classList.remove('table-active'));

                // Add highlight to clicked row
                this.classList.add('table-active');
            });
        });
    });
}

// ================================================
// Smooth Scroll
// ================================================

/**
 * Initialize smooth scroll for anchor links
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#' && href !== '#!') {
                e.preventDefault();
                const target = document.querySelector(href);

                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

// ================================================
// Auto-dismiss Alerts
// ================================================

/**
 * Auto-dismiss flash messages after 5 seconds
 */
function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');

    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-permanent')) {
            setTimeout(() => {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}

// ================================================
// Animated Counter
// ================================================

/**
 * Animate numbers counting up
 * @param {HTMLElement} element - Element containing the number
 * @param {number} start - Start value
 * @param {number} end - End value
 * @param {number} duration - Animation duration in ms
 */
function animateCounter(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);

        const value = Math.floor(progress * (end - start) + start);
        element.textContent = value.toLocaleString();

        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

/**
 * Initialize counter animations for stats cards
 */
function initStatCounters() {
    const statCards = document.querySelectorAll('.stats-card h3, .financial-card h3');

    statCards.forEach(card => {
        const text = card.textContent.trim();
        const number = parseFloat(text.replace(/[^0-9.-]/g, ''));

        if (!isNaN(number)) {
            // Use Intersection Observer to trigger animation when visible
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        animateCounter(card, 0, number, 1000);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            observer.observe(card);
        }
    });
}

// ================================================
// Dark Mode Toggle (Optional Enhancement)
// ================================================

/**
 * Toggle dark mode
 */
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
}

/**
 * Initialize dark mode from localStorage
 */
function initDarkMode() {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.body.classList.add('dark-mode');
    }
}

// ================================================
// Enhanced Modal Animations
// ================================================

/**
 * Add enhanced animations to modals
 */
function initModalEnhancements() {
    const modals = document.querySelectorAll('.modal');

    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            this.querySelector('.modal-dialog')?.classList.add('modal-show-animation');
        });

        modal.addEventListener('hidden.bs.modal', function() {
            this.querySelector('.modal-dialog')?.classList.remove('modal-show-animation');
        });
    });
}

// ================================================
// Initialize on Page Load
// ================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all enhancements
    initFormValidation();
    initSmoothScroll();
    initAutoDismissAlerts();
    initTableRowHighlight();
    initModalEnhancements();
    // initDarkMode(); // Uncomment to enable dark mode

    // Initialize stat counters if they exist
    if (document.querySelector('.stats-card, .financial-card')) {
        // Delay counter animation slightly for better UX
        setTimeout(initStatCounters, 300);
    }

    // Hide any loading overlays that might be present
    hideLoading();

    // Add CSS for shake animation
    if (!document.getElementById('shake-animation-style')) {
        const style = document.createElement('style');
        style.id = 'shake-animation-style';
        style.textContent = `
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-10px); }
                75% { transform: translateX(10px); }
            }
            .shake {
                animation: shake 0.5s;
                border-color: var(--danger-red) !important;
            }
            .table-active {
                background-color: var(--delta-light-blue) !important;
            }
        `;
        document.head.appendChild(style);
    }
});

// ================================================
// Export functions for use in templates
// ================================================

window.deltaApp = {
    initTableSearch,
    showLoading,
    hideLoading,
    showToast,
    confirmDeleteAction,
    toggleDarkMode
};
