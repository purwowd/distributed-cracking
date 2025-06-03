/**
 * Agent form functionality
 * Handles API key generation for agent registration
 */
document.addEventListener('DOMContentLoaded', function() {
    const generateKeyBtn = document.getElementById('generate-key');
    const apiKeyInput = document.getElementById('api_key');
    
    if (generateKeyBtn && apiKeyInput) {
        generateKeyBtn.addEventListener('click', function() {
            // Generate a random API key
            const randomKey = 'api_key_' + Array(24)
                .fill(0)
                .map(() => Math.random().toString(36).charAt(2))
                .join('');
            
            apiKeyInput.value = randomKey;
        });
    }
});
