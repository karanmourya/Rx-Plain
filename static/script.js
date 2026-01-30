const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const submitBtn = document.getElementById('submitBtn');
const resultsSection = document.getElementById('resultsSection');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.background = '#eef0ff';
    dropZone.style.borderColor = '#764ba2';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.style.background = '#f8f9ff';
    dropZone.style.borderColor = '#667eea';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.background = '#f8f9ff';
    dropZone.style.borderColor = '#667eea';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        updateDropZoneText(files[0].name);
    }
});

fileInput.addEventListener('change', (e) => {
    if (fileInput.files.length > 0) {
        updateDropZoneText(fileInput.files[0].name);
    }
});

function updateDropZoneText(filename) {
    const dropZoneText = dropZone.querySelector('p');
    dropZoneText.textContent = `Selected: ${filename}`;
}

uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file first');
        return;
    }
    
    const language = document.getElementById('language').value;
    
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-text').classList.add('hidden');
    submitBtn.querySelector('.loading').classList.remove('hidden');
    resultsSection.classList.add('hidden');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis failed');
        }
        
        const data = await response.json();
        
        document.getElementById('extractedData').textContent = data.extracted_data;
        document.getElementById('ragContext').textContent = data.rag_context;
        document.getElementById('finalResponse').textContent = data.final_response;
        
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error('Error:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').classList.remove('hidden');
        submitBtn.querySelector('.loading').classList.add('hidden');
    }
});
