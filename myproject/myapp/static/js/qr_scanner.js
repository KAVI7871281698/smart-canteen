document.addEventListener('DOMContentLoaded', function() {
    const qrScannerBtn = document.getElementById('qr-scanner-btn');
    const qrVideo = document.getElementById('qr-video');
    const qrCanvas = document.createElement('canvas');
    const qrResult = document.getElementById('qr-result');
    
    qrScannerBtn.addEventListener('click', async function() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'environment' } 
            });
            
            qrVideo.srcObject = stream;
            qrVideo.classList.remove('d-none');
            qrVideo.play();
            
            function scanQR() {
                if (qrVideo.readyState === qrVideo.HAVE_ENOUGH_DATA) {
                    qrCanvas.height = qrVideo.videoHeight;
                    qrCanvas.width = qrVideo.videoWidth;
                    
                    const ctx = qrCanvas.getContext('2d');
                    ctx.drawImage(qrVideo, 0, 0, qrCanvas.width, qrCanvas.height);
                    
                    try {
                        const imageData = ctx.getImageData(0, 0, qrCanvas.width, qrCanvas.height);
                        const code = jsQR(imageData.data, imageData.width, imageData.height, {
                            inversionAttempts: 'dontInvert',
                        });
                        
                        if (code) {
                            const data = code.data.split(',');
                            const userId = data[0].split(':')[1];
                            document.getElementById('user_id').value = userId;
                            document.getElementById('pin').focus();
                            stopScanner(stream);
                        } else {
                            requestAnimationFrame(scanQR);
                        }
                    } catch (e) {
                        console.error("QR scanning error:", e);
                        requestAnimationFrame(scanQR);
                    }
                } else {
                    requestAnimationFrame(scanQR);
                }
            }
            
            scanQR();
        } catch (err) {
            console.error("Error accessing camera:", err);
            alert("Could not access camera. Please ensure you've granted camera permissions.");
        }
    });
    
    function stopScanner(stream) {
        stream.getTracks().forEach(track => track.stop());
        qrVideo.classList.add('d-none');
    }
});