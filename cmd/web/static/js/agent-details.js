/**
 * Agent Details JavaScript
 * Handles UI interactions for the agent detail page
 */

/**
 * Toggle visibility of GPU details section
 * @param {string} id - The ID of the element to toggle
 */
function toggleDetails(id) {
    const element = document.getElementById(id);
    if (element.classList.contains('hidden')) {
        element.classList.remove('hidden');
    } else {
        element.classList.add('hidden');
    }
}
