async function convertVideo() {
    const urlInput = document.getElementById('urlInput');
    const convertBtn = document.getElementById('convertBtn');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const statusDiv = document.getElementById('statusMessage');
    const videoTitle = document.getElementById('videoTitle');
    const thumbnail = document.getElementById('thumbnail');
    const downloadLink = document.getElementById('downloadLink');

    const url = urlInput.value.trim();

    // Reset UI
    statusDiv.textContent = '';
    resultDiv.classList.add('hidden');

    if (!url) {
        statusDiv.textContent = 'Please enter a valid YouTube URL';
        return;
    }

    // Set Loading State
    convertBtn.disabled = true;
    convertBtn.style.opacity = '0.7';
    loadingDiv.classList.remove('hidden');

    try {
        const response = await fetch('/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // Update Result UI
            videoTitle.textContent = data.title;
            thumbnail.src = data.thumbnail;
            downloadLink.href = data.download_url;
            downloadLink.download = `${data.title}.mp3`;

            resultDiv.classList.remove('hidden');
        } else {
            throw new Error(data.error || 'Conversion failed');
        }

    } catch (error) {
        statusDiv.textContent = `Error: ${error.message}`;
    } finally {
        // Reset Loading State
        loadingDiv.classList.add('hidden');
        convertBtn.disabled = false;
        convertBtn.style.opacity = '1';
    }
}

// Allow Enter key to trigger conversion
document.getElementById('urlInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        convertVideo();
    }
});
