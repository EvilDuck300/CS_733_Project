// Main JavaScript for Presentation Generator

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('inputForm');
    const fileInput = document.getElementById('pdfFile');
    const fileNameDisplay = document.getElementById('fileName');
    const descriptionTextarea = document.getElementById('description');
    const charCount = document.getElementById('charCount');
    const submitBtn = document.getElementById('submitBtn');
    const statusMessage = document.getElementById('statusMessage');

    // File input handling
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                fileNameDisplay.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
                fileNameDisplay.classList.add('show');
            } else {
                fileNameDisplay.classList.remove('show');
            }
        });

        // Drag and drop functionality
        const fileUploadLabel = document.querySelector('.file-upload-label');
        if (fileUploadLabel) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                fileUploadLabel.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                fileUploadLabel.addEventListener(eventName, function() {
                    fileUploadLabel.style.borderColor = '#667eea';
                    fileUploadLabel.style.background = '#f0f4ff';
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                fileUploadLabel.addEventListener(eventName, function() {
                    fileUploadLabel.style.borderColor = '';
                    fileUploadLabel.style.background = '';
                }, false);
            });

            fileUploadLabel.addEventListener('drop', function(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    fileInput.dispatchEvent(new Event('change'));
                }
            }, false);
        }
    }

    // Character count for description
    if (descriptionTextarea && charCount) {
        descriptionTextarea.addEventListener('input', function() {
            const length = this.value.length;
            charCount.textContent = length;
            
            const charCountDiv = charCount.parentElement;
            charCountDiv.classList.remove('warning', 'error');
            
            if (length > 900) {
                charCountDiv.classList.add('error');
            } else if (length > 800) {
                charCountDiv.classList.add('warning');
            }
        });
    }

    // Form submission
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Validate form
            if (!fileInput.files || fileInput.files.length === 0) {
                showStatus('error', 'Please select a PDF file');
                return;
            }

            const audienceType = document.getElementById('audienceType').value;
            if (!audienceType) {
                showStatus('error', 'Please select an audience type');
                return;
            }

            const description = descriptionTextarea.value.trim();
            if (!description) {
                showStatus('error', 'Please enter a description');
                return;
            }

            if (description.length > 1000) {
                showStatus('error', 'Description exceeds 1000 characters');
                return;
            }

            // Disable submit button and show loading
            submitBtn.disabled = true;
            const btnText = submitBtn.querySelector('.btn-text');
            const btnLoader = submitBtn.querySelector('.btn-loader');
            if (btnText) btnText.style.display = 'none';
            if (btnLoader) btnLoader.style.display = 'inline-block';

            // Create form data
            const formData = new FormData();
            formData.append('pdfFile', fileInput.files[0]);
            formData.append('audienceType', audienceType);
            formData.append('description', description);

            try {
                const response = await fetch('/api/submit', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    showStatus('success', 'Form submitted successfully! Processing your request...');
                    
                    // Redirect to review page after a short delay
                    setTimeout(() => {
                        window.location.href = `/review/${data.submission_id}`;
                    }, 2000);
                } else {
                    showStatus('error', data.error || 'An error occurred while submitting the form');
                    submitBtn.disabled = false;
                    if (btnText) btnText.style.display = 'inline';
                    if (btnLoader) btnLoader.style.display = 'none';
                }
            } catch (error) {
                showStatus('error', 'Network error: ' + error.message);
                submitBtn.disabled = false;
                if (btnText) btnText.style.display = 'inline';
                if (btnLoader) btnLoader.style.display = 'none';
            }
        });
    }

    function showStatus(type, message) {
        statusMessage.textContent = message;
        statusMessage.className = `status-message ${type}`;
        statusMessage.style.display = 'block';

        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                statusMessage.style.display = 'none';
            }, 5000);
        }
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
});

