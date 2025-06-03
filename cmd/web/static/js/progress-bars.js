/**
 * Progress Bar Handler
 * 
 * Script untuk mengatur lebar progress bar di seluruh aplikasi
 * Versi terbaru: Menggunakan pendekatan berbasis kelas CSS untuk menghindari masalah linting CSS
 */
document.addEventListener('DOMContentLoaded', function() {
    // Tangani link hasil dengan data attribute
    const resultsLinks = document.querySelectorAll('.results-link');
    resultsLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const taskId = this.getAttribute('data-task-id');
            if (taskId) {
                window.location.href = '/results?task_id=' + taskId;
            }
        });
    });
    
    // Fungsi untuk mengatur semua jenis progress bar
    function setAllProgressBars() {
        // Tangani progress bar task dengan kelas progress-data
        const progressBars = document.querySelectorAll('.h-2\\.5.bg-blue-600');
        progressBars.forEach(function(bar) {
            // Cari elemen dengan kelas progress-data terdekat
            const container = bar.closest('.mb-4') || bar.parentElement.parentElement;
            if (container) {
                const progressDataElement = container.querySelector('.progress-data');
                if (progressDataElement) {
                    const progressValue = parseFloat(progressDataElement.textContent);
                    if (!isNaN(progressValue)) {
                        bar.style.width = progressValue + '%';
                    }
                } else {
                    // Fallback: cari elemen teks persentase terdekat
                    const percentText = container.querySelector('.text-xs.text-gray-500');
                    if (percentText) {
                        // Ekstrak angka dari teks (misalnya "50.5%" menjadi 50.5)
                        const percentMatch = percentText.textContent.match(/([\d.]+)%/);
                        if (percentMatch && percentMatch[1]) {
                            const percentValue = parseFloat(percentMatch[1]);
                            if (!isNaN(percentValue)) {
                                bar.style.width = percentValue + '%';
                            }
                        }
                    }
                }
            }
        });
        
        // Tangani progress bar recovery dengan kelas recovery-progress-bar
        const recoveryProgressBars = document.querySelectorAll('.recovery-progress-bar');
        recoveryProgressBars.forEach(function(bar) {
            // Cari elemen dengan kelas recovery-data terdekat
            const container = bar.closest('.mb-3') || bar.parentElement.parentElement;
            if (container) {
                const recoveryDataElement = container.querySelector('.recovery-data');
                if (recoveryDataElement) {
                    const recoveryValue = parseFloat(recoveryDataElement.textContent);
                    if (!isNaN(recoveryValue)) {
                        bar.style.width = recoveryValue + '%';
                    }
                } else {
                    // Fallback: cari elemen teks persentase terdekat
                    const percentText = container.querySelector('.text-xs.text-gray-500');
                    if (percentText) {
                        // Ekstrak angka dari teks
                        const percentMatch = percentText.textContent.match(/([\d.]+)%/);
                        if (percentMatch && percentMatch[1]) {
                            const percentValue = parseFloat(percentMatch[1]);
                            if (!isNaN(percentValue)) {
                                bar.style.width = percentValue + '%';
                            }
                        }
                    }
                }
            }
        });
        
        // Tangani progress bar agent detail dengan ID statis (pendekatan terbaru)
        const agentProgressIndicator = document.getElementById('agent-progress-indicator');
        if (agentProgressIndicator) {
            const progressDataElement = document.getElementById('agent-progress-data');
            if (progressDataElement) {
                const progressValue = parseFloat(progressDataElement.textContent);
                if (!isNaN(progressValue)) {
                    agentProgressIndicator.style.width = progressValue + '%';
                }
            }
        }
        
        // Tangani progress bar agent detail dengan ID lama (untuk kompatibilitas)
        const agentProgressBar = document.getElementById('agent-progress-bar');
        if (agentProgressBar) {
            // Cari elemen teks persentase terdekat
            const container = agentProgressBar.closest('.mb-3') || agentProgressBar.parentElement.parentElement;
            if (container) {
                const percentText = container.querySelector('.text-xs.text-gray-500');
                if (percentText) {
                    // Ekstrak angka dari teks
                    const percentMatch = percentText.textContent.match(/([\d.]+)%/);
                    if (percentMatch && percentMatch[1]) {
                        const percentValue = parseFloat(percentMatch[1]);
                        if (!isNaN(percentValue)) {
                            agentProgressBar.style.width = percentValue + '%';
                        }
                    }
                }
            }
        }
        
        // Tangani progress bar lama yang mungkin masih ada di halaman lain
        const oldProgressBars = document.querySelectorAll('.progress-bar');
        oldProgressBars.forEach(function(bar) {
            if (bar.hasAttribute('data-width')) {
                const width = bar.getAttribute('data-width');
                if (width) {
                    bar.style.width = width + '%';
                }
            }
        });
    }
    
    // Jalankan fungsi saat halaman dimuat
    setAllProgressBars();
    
    // Tambahkan observer untuk memantau perubahan DOM (untuk konten yang dimuat secara dinamis)
    const observer = new MutationObserver(function(mutations) {
        let hasNewProgressBar = false;
        
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        // Cek apakah ada progress bar baru
                        if (node.id === 'agent-progress-indicator' || node.id === 'agent-progress-bar' ||
                            node.classList && (node.classList.contains('progress-bar') || 
                                              node.classList.contains('task-progress-bar') || 
                                              node.classList.contains('recovery-progress-bar')) || 
                            node.querySelector('.progress-data, .recovery-data, .progress-bar, .task-progress-bar, .recovery-progress-bar, #agent-progress-indicator, #agent-progress-bar')) {
                            hasNewProgressBar = true;
                        }
                    }
                });
            }
        });
        
        // Jika ada progress bar baru, atur lebarnya
        if (hasNewProgressBar) {
            setAllProgressBars();
        }
    });
    
    // Konfigurasi observer
    const config = { childList: true, subtree: true };
    
    // Mulai observasi
    observer.observe(document.body, config);
});
