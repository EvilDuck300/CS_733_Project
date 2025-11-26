// File upload handling
const pdfFileInput = document.getElementById('pdfFile');
const fileNameDisplay = document.getElementById('fileName');
const fileUploadLabel = document.querySelector('.file-upload-label');

pdfFileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        // Validate file type
        if (file.type !== 'application/pdf') {
            showStatus('Please select a valid PDF file.', 'error');
            pdfFileInput.value = '';
            return;
        }

        // Validate file size (50MB)
        const maxSize = 50 * 1024 * 1024; // 50MB in bytes
        if (file.size > maxSize) {
            showStatus('File size exceeds 50MB limit. Please choose a smaller file.', 'error');
            pdfFileInput.value = '';
            return;
        }

        // Display file name
        fileNameDisplay.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
        fileNameDisplay.classList.add('show');
        fileUploadLabel.style.borderColor = '#10b981';
        fileUploadLabel.style.background = '#f0fdf4';
    } else {
        fileNameDisplay.classList.remove('show');
        fileUploadLabel.style.borderColor = '#667eea';
        fileUploadLabel.style.background = '#f8f9ff';
    }
});

// Drag and drop functionality
const fileUploadContainer = document.querySelector('.file-upload-container');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    fileUploadContainer.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    fileUploadContainer.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    fileUploadContainer.addEventListener(eventName, unhighlight, false);
});

function highlight(e) {
    fileUploadLabel.style.borderColor = '#764ba2';
    fileUploadLabel.style.background = '#f0f2ff';
}

function unhighlight(e) {
    fileUploadLabel.style.borderColor = '#667eea';
    fileUploadLabel.style.background = '#f8f9ff';
}

fileUploadContainer.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        pdfFileInput.files = files;
        pdfFileInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

// Character count for description
const descriptionTextarea = document.getElementById('description');
const charCount = document.getElementById('charCount');
const maxChars = 1000;

descriptionTextarea.addEventListener('input', function() {
    const currentLength = this.value.length;
    charCount.textContent = currentLength;
    
    const charCountElement = charCount.parentElement;
    charCountElement.classList.remove('warning', 'error');
    
    if (currentLength > maxChars * 0.9) {
        charCountElement.classList.add('warning');
    }
    if (currentLength > maxChars) {
        charCountElement.classList.add('error');
        this.value = this.value.substring(0, maxChars);
        charCount.textContent = maxChars;
    }
});

// Form submission
const inputForm = document.getElementById('inputForm');
const submitBtn = document.getElementById('submitBtn');

inputForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Validate form
    if (!pdfFileInput.files[0]) {
        showStatus('Please select a PDF file.', 'error');
        return;
    }

    if (!document.getElementById('audienceType').value) {
        showStatus('Please select an audience type.', 'error');
        return;
    }

    if (!descriptionTextarea.value.trim()) {
        showStatus('Please enter a description.', 'error');
        return;
    }

    // Disable submit button and show loading state
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').style.display = 'none';
    submitBtn.querySelector('.btn-loader').style.display = 'inline';

    // Create FormData
    const formData = new FormData();
    formData.append('pdfFile', pdfFileInput.files[0]);
    formData.append('audienceType', document.getElementById('audienceType').value);
    formData.append('description', descriptionTextarea.value.trim());

    try {
        const response = await fetch('/api/submit', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showStatus('Form submitted successfully! Processing your request...', 'success');
            // Reset form after successful submission
            setTimeout(() => {
                inputForm.reset();
                fileNameDisplay.classList.remove('show');
                charCount.textContent = '0';
                fileUploadLabel.style.borderColor = '#667eea';
                fileUploadLabel.style.background = '#f8f9ff';
            }, 2000);
        } else {
            showStatus(data.error || 'An error occurred. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showStatus('Network error. Please check your connection and try again.', 'error');
    } finally {
        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').style.display = 'inline';
        submitBtn.querySelector('.btn-loader').style.display = 'none';
    }
});

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showStatus(message, type) {
    const statusMessage = document.getElementById('statusMessage');
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 5000);
}

