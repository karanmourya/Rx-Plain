const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const submitBtn = document.getElementById('submitBtn');
const resultsSection = document.getElementById('resultsSection');
const progressSection = document.getElementById('progressSection');
const progressBar = document.getElementById('progressBar');
const progressStatus = document.getElementById('progressStatus');

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
    progressSection.classList.remove('hidden');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);
    
    try {
        const response = await fetch('/analyze-stream', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullResponse = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        switch (data.step) {
                            case 'extracting':
                                updateProgress(20, data.message);
                                break;
                            case 'extracted':
                                document.getElementById('extractedData').innerHTML = marked.parse(data.data);
                                break;
                            case 'rag':
                                updateProgress(40, data.message);
                                break;
                            case 'rag_done':
                                document.getElementById('ragContext').innerHTML = marked.parse(data.data);
                                updateProgress(60, 'Guidelines retrieved');
                                break;
                            case 'generating':
                                updateProgress(80, data.message);
                                resultsSection.classList.remove('hidden');
                                break;
                            case 'streaming':
                                fullResponse += data.content;
                                document.getElementById('finalResponse').innerHTML = marked.parse(fullResponse);
                                resultsSection.classList.remove('hidden');
                                resultsSection.scrollIntoView({ behavior: 'smooth', block: 'end' });
                                break;
                            case 'done':
                                updateProgress(100, 'Analysis complete!');
                                break;
                            case 'error':
                                throw new Error(data.message);
                        }
                    } catch (parseError) {
                        console.error('Error parsing SSE data:', parseError);
                    }
                }
            }
        }
        
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error('Error:', error);
    } finally {
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-text').classList.remove('hidden');
        submitBtn.querySelector('.loading').classList.add('hidden');
        setTimeout(() => {
            progressSection.classList.add('hidden');
        }, 2000);
    }
});

function updateProgress(percent, message) {
    progressBar.style.width = `${percent}%`;
    progressStatus.textContent = message;
}
