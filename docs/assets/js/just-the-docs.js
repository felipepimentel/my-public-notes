---
    layout: null
---

    // Minimal JS to ensure Jekyll processes this file
    // This helps ensure that CSS assets are loaded correctly

    document.addEventListener('DOMContentLoaded', function () {
        console.log('Just the Docs theme initialized');

        // Fix 404 page issues with CSS
        if (window.location.pathname.includes('404.html') || document.body.classList.contains('not-found')) {
            const baseUrl = '{{ site.baseurl }}';

            // Ensure proper CSS loading
            const linkCSS = document.createElement('link');
            linkCSS.rel = 'stylesheet';
            linkCSS.href = baseUrl + '/assets/css/custom.css';
            document.head.appendChild(linkCSS);

            // Ensure proper theme CSS loading
            const linkThemeCSS = document.createElement('link');
            linkThemeCSS.rel = 'stylesheet';
            linkThemeCSS.href = baseUrl + '/assets/css/just-the-docs.css';
            document.head.appendChild(linkThemeCSS);

            // Add class to body
            document.body.classList.add('page-not-found');
        }
    }); 