/**
 * Results page functionality for the Distributed Hashcat Cracking system
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize copy buttons
    initCopyButtons();
    
    // Initialize export functionality
    initExportButtons();
    
    // Initialize filter form
    initFilterForm();
});

/**
 * Initialize clipboard copy functionality for result items
 */
function initCopyButtons() {
    // Copy hash button
    document.querySelectorAll('.copy-hash').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const hash = this.getAttribute('data-hash');
            copyToClipboard(hash, 'Hash copied to clipboard!');
        });
    });
    
    // Copy plaintext button
    document.querySelectorAll('.copy-plaintext').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const plaintext = this.getAttribute('data-plaintext');
            copyToClipboard(plaintext, 'Password copied to clipboard!');
        });
    });
    
    // Copy both button
    document.querySelectorAll('.copy-both').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const hash = this.getAttribute('data-hash');
            const plaintext = this.getAttribute('data-plaintext');
            const text = `${hash}:${plaintext}`;
            copyToClipboard(text, 'Hash:Password copied to clipboard!');
        });
    });
}

/**
 * Copy text to clipboard and show a toast notification
 * @param {string} text - Text to copy
 * @param {string} message - Success message to display
 */
function copyToClipboard(text, message) {
    navigator.clipboard.writeText(text).then(() => {
        // Create toast notification
        const toastEl = document.createElement('div');
        toastEl.className = 'toast align-items-center text-white bg-success border-0';
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-clipboard-check"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
            container.appendChild(toastEl);
        } else {
            toastContainer.appendChild(toastEl);
        }
        
        const toast = new bootstrap.Toast(toastEl, {
            delay: 2000
        });
        toast.show();
        
        // Remove toast after it's hidden
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        alert('Failed to copy to clipboard');
    });
}

/**
 * Initialize export functionality
 */
function initExportButtons() {
    const exportCsvBtn = document.getElementById('export-csv');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function(e) {
            e.preventDefault();
            exportResultsToCSV();
        });
    }
    
    const exportTxtBtn = document.getElementById('export-txt');
    if (exportTxtBtn) {
        exportTxtBtn.addEventListener('click', function(e) {
            e.preventDefault();
            exportResultsToTXT();
        });
    }
}

/**
 * Export results to CSV file
 */
function exportResultsToCSV() {
    const table = document.querySelector('.results-table');
    if (!table) return;
    
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    if (rows.length === 0) {
        alert('No results to export');
        return;
    }
    
    let csvContent = 'Hash,Plaintext,Task ID,Cracked At\n';
    
    rows.forEach(row => {
        const cells = Array.from(row.querySelectorAll('td'));
        if (cells.length >= 4) {
            const hash = cells[0].getAttribute('data-hash') || cells[0].textContent.trim();
            const plaintext = cells[1].textContent.trim();
            const taskId = cells[2].querySelector('a') ? cells[2].querySelector('a').getAttribute('href').split('/').pop() : '';
            const crackedAt = cells[3].textContent.trim();
            
            csvContent += `"${hash}","${plaintext}","${taskId}","${crackedAt}"\n`;
        }
    });
    
    downloadFile(csvContent, 'hashcat-results.csv', 'text/csv');
}

/**
 * Export results to TXT file (hash:password format)
 */
function exportResultsToTXT() {
    const table = document.querySelector('.results-table');
    if (!table) return;
    
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    if (rows.length === 0) {
        alert('No results to export');
        return;
    }
    
    let txtContent = '';
    
    rows.forEach(row => {
        const cells = Array.from(row.querySelectorAll('td'));
        if (cells.length >= 2) {
            const hash = cells[0].getAttribute('data-hash') || cells[0].textContent.trim();
            const plaintext = cells[1].textContent.trim();
            
            txtContent += `${hash}:${plaintext}\n`;
        }
    });
    
    downloadFile(txtContent, 'hashcat-results.txt', 'text/plain');
}

/**
 * Download content as a file
 * @param {string} content - File content
 * @param {string} fileName - Name of the file
 * @param {string} contentType - MIME type of the file
 */
function downloadFile(content, fileName, contentType) {
    const a = document.createElement('a');
    const file = new Blob([content], {type: contentType});
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(a.href);
}

/**
 * Initialize filter form functionality
 */
function initFilterForm() {
    const filterForm = document.getElementById('filter-form');
    if (!filterForm) return;
    
    // Clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const inputs = filterForm.querySelectorAll('input, select');
            inputs.forEach(input => {
                input.value = '';
            });
            filterForm.submit();
        });
    }
}
