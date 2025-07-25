// assets/dropdown_tooltips.js

// This function will be called whenever the dropdown options are added to the DOM.
function addTitlesToDropdownOptions(mutationList, observer) {
    const dropdownOptions = document.querySelectorAll('.Select-option');

    dropdownOptions.forEach(option => {
        // Check if the option already has a title to avoid redundant setting
        // and to prevent overwriting if another script might set it.
        if (!option.hasAttribute('title')) {
            const fullText = option.textContent.trim();
            option.setAttribute('title', fullText);
            console.log('Added tooltip for:', fullText); // Uncomment for debugging
        }
    });
}

// Create a MutationObserver instance
// This observer will watch for changes in the DOM, specifically when child nodes are added.
const observer = new MutationObserver(addTitlesToDropdownOptions);

// Define the configuration for the observer
// childList: true means to observe additions/removals of direct children
// subtree: true means to observe all descendants, not just direct children
const config = { childList: true, subtree: true };

// Get the main Dash app container. This is typically 'react-entry-point' or 'dash-app-container'.
// If your layout.py uses a different ID for the outermost div, update this.
const appContainer = document.getElementById('dash-app-container') || document.getElementById('react-entry-point');

if (appContainer) {
    // Start observing the app container for changes
    // This will catch when the dropdown menu (and its options) are added to the page.
    observer.observe(appContainer, config);
    // console.log('MutationObserver started for dropdown tooltips.'); // Uncomment for debugging

    // Also, try to apply tooltips immediately on load in case the dropdown is
    // pre-rendered or updated quickly by a callback.
    addTitlesToDropdownOptions();
} else {
    // Fallback if the main app container isn't immediately found.
    // This might happen if the app takes a moment to load.
    // We can observe the body or just log a warning.
    console.warn("Dash app container not found immediately. Tooltip observer might start late.");
    // As a last resort, observe the entire document body if the app container ID is unknown/missing
    document.addEventListener('DOMContentLoaded', () => {
        const fallbackContainer = document.getElementById('dash-app-container') || document.getElementById('react-entry-point');
        if (fallbackContainer) {
             observer.observe(fallbackContainer, config);
             addTitlesToDropdownOptions();
        } else {
            console.error("Could not find Dash app container for MutationObserver. Dropdown tooltips may not work.");
        }
    });
}
