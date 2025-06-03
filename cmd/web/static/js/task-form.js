/**
 * Task form functionality
 * Handles attack mode selection and dynamic form fields visibility
 */
document.addEventListener('DOMContentLoaded', function() {
    const attackModeSelect = document.getElementById('attack_mode');
    
    if (attackModeSelect) {
        // Show/hide attack mode specific fields
        attackModeSelect.addEventListener('change', function() {
            const attackMode = parseInt(this.value);
            const wordlistSection = document.getElementById('wordlist_section');
            const ruleSection = document.getElementById('rule_section');
            const maskSection = document.getElementById('mask_section');
            
            if (!wordlistSection || !ruleSection || !maskSection) return;
            
            // Reset visibility
            wordlistSection.classList.add('hidden');
            ruleSection.classList.add('hidden');
            maskSection.classList.add('hidden');
            
            // Show relevant sections based on attack mode
            switch(attackMode) {
                case 0: // Dictionary
                    wordlistSection.classList.remove('hidden');
                    ruleSection.classList.remove('hidden');
                    break;
                case 1: // Combination
                    wordlistSection.classList.remove('hidden');
                    break;
                case 3: // Brute Force/Mask
                    maskSection.classList.remove('hidden');
                    break;
                case 6: // Hybrid Wordlist + Mask
                    wordlistSection.classList.remove('hidden');
                    maskSection.classList.remove('hidden');
                    break;
                case 7: // Hybrid Mask + Wordlist
                    wordlistSection.classList.remove('hidden');
                    maskSection.classList.remove('hidden');
                    break;
            }
        });
        
        // Trigger change event to set initial visibility
        attackModeSelect.dispatchEvent(new Event('change'));
    }
    
    // WPA form validation (can be expanded later)
    const wpaForm = document.querySelector('form[action="/tasks/new-wpa"]');
    if (wpaForm) {
        // Add form validation logic here if needed
    }
});
