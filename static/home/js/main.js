/* ==========================================================================
   IPCO Portal — main.js
   --------------------------------------------------------------------------
   Vanilla ES6, modular IIFE sections. Hooks expected by Django templates:
     #theme-switcher / #theme-switcher-toggle
     #site-search / .header-search(.is-open) / #header-search-toggle / .search-close
     #main-nav / .nav-toggle / .nav-backdrop
     .nav-item-dropdown / .dropdown-toggle / .dropdown-panel
     [data-reveal]  ·  .announcement-card-button / .announcement-modal
     [data-copy-link]  ·  .reading-progress-fill  ·  .hero-story-link
   Theme persistence key: "ikco-theme" (light | dark | system)
   ========================================================================== */

(function () {
    "use strict";

    var $ = function (sel, ctx) {
        return (ctx || document).querySelector(sel);
    };
    var $$ = function (sel, ctx) {
        return Array.prototype.slice.call((ctx || document).querySelectorAll(sel));
    };
    var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* -----------------------------------------------------------------------
     * Theme manager
     * --------------------------------------------------------------------- */
    var THEME_KEY = "ikco-theme";
    var root = document.documentElement;
    var colorSchemeMql = window.matchMedia("(prefers-color-scheme: dark)");

    function getStoredTheme() {
        try {
            return localStorage.getItem(THEME_KEY) || "system";
        } catch (e) {
            return "system";
        }
    }

    function applyTheme(theme) {
        var resolved = theme === "system" ? (colorSchemeMql.matches ? "dark" : "light") : theme;
        root.setAttribute("data-theme", resolved);
    }

    function updateThemeIcon(theme) {
        var iconLight = $("#theme-icon-light");
        var iconDark = $("#theme-icon-dark");
        var resolved = theme === "system" ? (colorSchemeMql.matches ? "dark" : "light") : theme;
        if (iconLight && iconDark) {
            iconLight.style.display = resolved === "dark" ? "none" : "block";
            iconDark.style.display = resolved === "dark" ? "block" : "none";
        }
    }

    function setTheme(theme) {
        try {
            localStorage.setItem(THEME_KEY, theme);
        } catch (e) { /* private mode */ }
        applyTheme(theme);
        updateThemeIcon(theme);
    }

    var themeToggle = $("#theme-switcher-toggle");

    updateThemeIcon(getStoredTheme());
    if (colorSchemeMql.addEventListener) {
        colorSchemeMql.addEventListener("change", function () {
            if (getStoredTheme() === "system") {
                applyTheme("system");
                updateThemeIcon("system");
            }
        });
    }
    if (themeToggle) {
        themeToggle.addEventListener("click", function (event) {
            event.stopPropagation();
            var currentTheme = getStoredTheme();
            var resolved = currentTheme === "system" ? (colorSchemeMql.matches ? "dark" : "light") : currentTheme;
            var nextTheme = resolved === "dark" ? "light" : "dark";
            setTheme(nextTheme);
        });
    }
    /* Unblock transitions now that the initial theme is painted. */
    requestAnimationFrame(function () {
        root.classList.remove("theme-init");
    });

    /* -----------------------------------------------------------------------
     * Header elevation on scroll
     * --------------------------------------------------------------------- */
    var header = $(".site-header");

    function updateHeaderState() {
        if (header) header.classList.toggle("scrolled", window.scrollY > 12);
    }

    updateHeaderState();
    window.addEventListener("scroll", updateHeaderState, {passive: true});

    /* -----------------------------------------------------------------------
     * Search overlay
     * The .header-search <form> itself becomes the full-screen scrim when
     * .is-open is present, so the same GET request stays intact.
     * --------------------------------------------------------------------- */
    var searchToggle = $("#header-search-toggle");
    var searchForm = $(".header-search");
    var searchInput = $("#site-search");
    var searchCloseBtn = $(".search-close");
    var lastFocusedBeforeSearch = null;

    function openSearch() {
        if (!searchForm) return;
        lastFocusedBeforeSearch = document.activeElement;
        searchForm.classList.add("is-open");
        document.body.classList.add("search-open");
        if (searchToggle) searchToggle.setAttribute("aria-expanded", "true");
        if (searchInput) {
            window.setTimeout(function () {
                searchInput.focus({preventScroll: true});
            }, 60);
        }
    }

    function closeSearch() {
        if (!searchForm || !searchForm.classList.contains("is-open")) return;
        searchForm.classList.remove("is-open");
        document.body.classList.remove("search-open");
        if (searchToggle) searchToggle.setAttribute("aria-expanded", "false");
        if (lastFocusedBeforeSearch && lastFocusedBeforeSearch.focus) {
            lastFocusedBeforeSearch.focus({preventScroll: true});
        }
    }

    if (searchToggle && searchForm) {
        searchToggle.addEventListener("click", function (event) {
            event.stopPropagation();
            if (searchForm.classList.contains("is-open")) {
                closeSearch();
            } else {
                openSearch();
            }
        });
    }
    if (searchForm) {
        /* Click on the scrim (the form itself) closes; inner panel swallows it. */
        searchForm.addEventListener("click", function (event) {
            if (event.target === searchForm) closeSearch();
        });
        var overlayPanel = $(".search-overlay-panel", searchForm);
        if (overlayPanel) {
            overlayPanel.addEventListener("click", function (event) {
                event.stopPropagation();
            });
        }
    }
    if (searchCloseBtn) {
        searchCloseBtn.addEventListener("click", closeSearch);
    }

    /* -----------------------------------------------------------------------
     * Mobile navigation drawer
     * --------------------------------------------------------------------- */
    var navToggle = $(".nav-toggle");
    var nav = $("#main-nav");

    function closeDrawer() {
        if (!nav) return;
        nav.classList.remove("open");
        document.body.classList.remove("nav-open");
        if (navToggle) navToggle.setAttribute("aria-expanded", "false");
        closeAllDropdowns(null);
    }

    if (navToggle && nav) {
        navToggle.addEventListener("click", function () {
            var isOpen = nav.classList.toggle("open");
            navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
            document.body.classList.toggle("nav-open", isOpen);
            if (!isOpen) closeAllDropdowns(null);
        });
    }

    var backdrop = $(".nav-backdrop");
    if (backdrop) backdrop.addEventListener("click", closeDrawer);

    /* -----------------------------------------------------------------------
     * Dropdown system (megamenu, notifications, account)
     *   click-to-toggle · outside-close · Escape-close · autofocus first item
     * --------------------------------------------------------------------- */
    var dropdownItems = $$(".nav-item-dropdown");

    function closeDropdown(item) {
        item.classList.remove("open");
        var button = $(".dropdown-toggle", item);
        if (button) button.setAttribute("aria-expanded", "false");
    }

    function closeAllDropdowns(except) {
        dropdownItems.forEach(function (item) {
            if (item !== except) closeDropdown(item);
        });
    }

    dropdownItems.forEach(function (item) {
        var button = $(".dropdown-toggle", item);
        if (!button) return;
        button.addEventListener("click", function (event) {
            event.stopPropagation();
            if (item.classList.contains("workgroups-nav-item") && window.matchMedia("(min-width: 901px)").matches) {
                return;
            }
            var wasOpen = item.classList.contains("open");
            closeAllDropdowns(item);
            if (wasOpen) {
                closeDropdown(item);
            } else {
                item.classList.add("open");
                button.setAttribute("aria-expanded", "true");
                var firstLink = item.querySelector(".dropdown-panel a, .dropdown-panel button");
                if (firstLink) firstLink.focus({preventScroll: true});
            }
        });
    });

    document.addEventListener("click", function (event) {
        closeAllDropdowns(null);
    });
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeAllDropdowns(null);
            closeDrawer();
            closeSearch();
            closeAnnouncementModal();
        }
    });

    /* -----------------------------------------------------------------------
     * Reveal on scroll — staggered per container, not per page
     * (fixes the original global-index delay that made late sections stutter)
     * --------------------------------------------------------------------- */
    var revealItems = $$("[data-reveal]");
    revealItems.forEach(function (item) {
        /* Delay is indexed within the parent, so each section animates as a group. */
        var siblings = item.parentElement ? $$("[data-reveal]", item.parentElement) : [item];
        var index = siblings.indexOf(item);
        item.style.setProperty("--reveal-delay", Math.min(index, 6) * 80 + "ms");
    });

    if ("IntersectionObserver" in window && !reducedMotion) {
        var revealObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {threshold: 0.12, rootMargin: "0px 0px -6% 0px"});
        revealItems.forEach(function (item) {
            revealObserver.observe(item);
        });
    } else {
        revealItems.forEach(function (item) {
            item.classList.add("is-visible");
        });
    }

    /* -----------------------------------------------------------------------
     * Light hero parallax — the featured story image drifts a few px.
     * rAF-throttled, disabled for touch / reduced-motion users.
     * --------------------------------------------------------------------- */
    var heroStage = $(".hero-shell");
    var heroImage = $(".hero-story-link img");
    if (heroStage && heroImage && !reducedMotion) {
        var ticking = false;
        window.addEventListener("scroll", function () {
            if (ticking) return;
            ticking = true;
            requestAnimationFrame(function () {
                var rect = heroStage.getBoundingClientRect();
                if (rect.bottom > 0 && rect.top < window.innerHeight) {
                    var progress = Math.min(Math.max(-rect.top / rect.height, 0), 1);
                    heroImage.style.transform = "translate3d(0," + (progress * 26).toFixed(1) + "px,0)";
                }
                ticking = false;
            });
        }, {passive: true});
    }

    /* -----------------------------------------------------------------------
     * Reading progress (news detail)
     * --------------------------------------------------------------------- */
    var progressFill = $(".reading-progress-fill");
    var articleBody = $(".news-detail");
    if (progressFill && articleBody) {
        var progressTicking = false;
        var updateProgress = function () {
            var rect = articleBody.getBoundingClientRect();
            var total = rect.height - window.innerHeight;
            var done = Math.min(Math.max(-rect.top / (total > 0 ? total : 1), 0), 1);
            progressFill.style.width = (done * 100).toFixed(2) + "%";
            progressTicking = false;
        };
        window.addEventListener("scroll", function () {
            if (!progressTicking) {
                progressTicking = true;
                requestAnimationFrame(updateProgress);
            }
        }, {passive: true});
        updateProgress();
    }

    /* -----------------------------------------------------------------------
     * Announcement lightbox
     * --------------------------------------------------------------------- */
    var announcementModal = $(".announcement-modal");
    var announcementModalImage = announcementModal && $(".announcement-modal-image", announcementModal);
    var announcementModalTitle = announcementModal && $(".announcement-modal-title", announcementModal);
    var announcementModalClose = announcementModal && $(".announcement-modal-close", announcementModal);
    var announcementButtons = $$(".announcement-card-button");

    function openAnnouncementModal(imageUrl, title) {
        if (!announcementModal || !announcementModalImage || !announcementModalTitle) return;
        announcementModalImage.src = imageUrl;
        announcementModalImage.alt = title;
        announcementModalTitle.textContent = title;
        announcementModal.classList.add("open");
        announcementModal.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
        if (announcementModalClose) announcementModalClose.focus({preventScroll: true});
    }

    function closeAnnouncementModal() {
        if (!announcementModal) return;
        announcementModal.classList.remove("open");
        announcementModal.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
        if (announcementModalImage) announcementModalImage.src = "";
        if (announcementModalTitle) announcementModalTitle.textContent = "";
    }

    announcementButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            openAnnouncementModal(button.dataset.imageUrl, button.dataset.title);
        });
    });
    if (announcementModal) {
        announcementModal.addEventListener("click", function (event) {
            if (event.target === announcementModal) closeAnnouncementModal();
        });
    }
    if (announcementModalClose) announcementModalClose.addEventListener("click", closeAnnouncementModal);

    /* -----------------------------------------------------------------------
     * Archive pages — command-palette morph search
     * The circular launcher blooms into a floating search panel (`.is-open`
     * on #archiveSearch). Open with click or Ctrl/Cmd+K; close with Esc, ×
     * or a click anywhere outside the field.
     * --------------------------------------------------------------------- */
    var archiveSearch = $("#archiveSearch");
    var archiveSearchTrigger = $("#archiveSearchTrigger");
    var archiveSearchInput = $("#archiveSearchInput");
    var archiveSearchClose = $("#archiveSearchClose");

    function openArchiveSearch() {
        if (!archiveSearch || archiveSearch.classList.contains("is-open")) return;
        archiveSearch.classList.add("is-open");
        if (archiveSearchTrigger) {
            archiveSearchTrigger.setAttribute("aria-expanded", "true");
            archiveSearchTrigger.setAttribute("tabindex", "-1");
        }
        if (archiveSearchInput) {
            window.setTimeout(function () {
                archiveSearchInput.focus({preventScroll: true});
            }, 80);
        }
    }

    function closeArchiveSearch() {
        if (!archiveSearch || !archiveSearch.classList.contains("is-open")) return;
        archiveSearch.classList.remove("is-open");
        if (archiveSearchTrigger) {
            archiveSearchTrigger.setAttribute("aria-expanded", "false");
            archiveSearchTrigger.removeAttribute("tabindex");
            archiveSearchTrigger.focus({preventScroll: true});
        }
    }

    if (archiveSearchTrigger) {
        archiveSearchTrigger.addEventListener("click", function (event) {
            if (!archiveSearch.classList.contains("is-open")) {
                event.preventDefault();
                openArchiveSearch();
            }
        });
    }

    if (archiveSearchClose) {
        archiveSearchClose.addEventListener("click", closeArchiveSearch);
    }

    document.addEventListener("click", function (event) {
        if (archiveSearch && archiveSearch.classList.contains("is-open") &&
            !archiveSearch.contains(event.target)) {
            closeArchiveSearch();
        }
    });

    document.addEventListener("keydown", function (event) {
        if ((event.metaKey || event.ctrlKey) && (event.key === "k" || event.key === "K")) {
            event.preventDefault();
            if (archiveSearch && !archiveSearch.classList.contains("is-open")) {
                openArchiveSearch();
            } else if (archiveSearchInput) {
                archiveSearchInput.focus({preventScroll: true});
            }
        }
        if (event.key === "Escape" && archiveSearch && archiveSearch.classList.contains("is-open")) {
            closeArchiveSearch();
        }
    });

    /* -----------------------------------------------------------------------
     * Copy article link (news detail share rail)
     * --------------------------------------------------------------------- */
    $$("[data-copy-link]").forEach(function (button) {
        button.addEventListener("click", function () {
            var url = button.getAttribute("data-copy-link");
            var done = function () {
                button.setAttribute("data-copied", "true");
                button.setAttribute("aria-label", "پیوند کپی شد");
                window.setTimeout(function () {
                    button.setAttribute("aria-label", "کپی پیوند خبر");
                    button.removeAttribute("data-copied");
                }, 1800);
            };
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(url).then(done).catch(function () {
                });
            } else {
                var temp = document.createElement("textarea");
                temp.value = url;
                document.body.appendChild(temp);
                temp.select();
                try {
                    document.execCommand("copy");
                    done();
                } catch (e) {
                }
                document.body.removeChild(temp);
            }
        });
    });
})();
