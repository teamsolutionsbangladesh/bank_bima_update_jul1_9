document.addEventListener("DOMContentLoaded", function () { // #codex
    const sidebar = document.querySelector(".sidebar"); // #codex
    if (!sidebar) return; // #codex

    const currentPath = normalizePath(window.location.pathname); // #codex
    const toggles = sidebar.querySelectorAll(".submenu-toggle"); // #codex
    const links = sidebar.querySelectorAll('a[href]:not(.submenu-toggle)'); // #codex

    function normalizePath(path) { // #codex
        if (!path) return "/"; // #codex
        const anchor = document.createElement("a"); // #codex
        anchor.href = path; // #codex
        let cleanPath = anchor.pathname || "/"; // #codex
        if (cleanPath.length > 1) cleanPath = cleanPath.replace(/\/+$/, ""); // #codex
        return cleanPath; // #codex
    } // #codex

    function closeSiblingMenus(menuItem) { // #codex
        const currentLevel = menuItem.parentElement; // #codex
        if (!currentLevel) return; // #codex
        currentLevel.querySelectorAll(":scope > .menu-item.has-submenu.open").forEach(function (openItem) { // #codex
            if (openItem !== menuItem && !openItem.classList.contains("active-branch")) { // #codex
                openItem.classList.remove("open"); // #codex
            } // #codex
        }); // #codex
    } // #codex

    function openParents(element) { // #codex
        let parentMenu = element.closest(".submenu"); // #codex
        while (parentMenu) { // #codex
            const parentItem = parentMenu.closest(".menu-item.has-submenu"); // #codex
            if (parentItem) { // #codex
                parentItem.classList.add("open", "active-branch"); // #codex
            } // #codex
            parentMenu = parentItem ? parentItem.parentElement.closest(".submenu") : null; // #codex
        } // #codex
    } // #codex

    function markActiveLink() { // #codex
        let bestMatch = null; // #codex
        let bestLength = -1; // #codex
        links.forEach(function (link) { // #codex
            const href = link.getAttribute("href"); // #codex
            if (!href || href === "#" || href.startsWith("javascript:")) return; // #codex
            const linkPath = normalizePath(href); // #codex
            const isExact = currentPath === linkPath; // #codex
            const isSection = linkPath !== "/" && currentPath.startsWith(linkPath + "/"); // #codex
            if ((isExact || isSection) && linkPath.length > bestLength) { // #codex
                bestMatch = link; // #codex
                bestLength = linkPath.length; // #codex
            } // #codex
        }); // #codex
        if (!bestMatch) return; // #codex
        bestMatch.classList.add("active-sidebar-link"); // #codex
        const activeItem = bestMatch.closest(".menu-item"); // #codex
        if (activeItem) activeItem.classList.add("active-item"); // #codex
        openParents(bestMatch); // #codex
        bestMatch.scrollIntoView({ block: "nearest" }); // #codex
    } // #codex

    toggles.forEach(function (toggle) { // #codex
        toggle.addEventListener("click", function (event) { // #codex
            event.preventDefault(); // #codex
            const parentItem = toggle.closest(".menu-item.has-submenu"); // #codex
            if (!parentItem) return; // #codex
            const shouldOpen = !parentItem.classList.contains("open"); // #codex
            closeSiblingMenus(parentItem); // #codex
            parentItem.classList.toggle("open", shouldOpen); // #codex
        }); // #codex
    }); // #codex

    markActiveLink(); // #codex
}); // #codex
