document.addEventListener('DOMContentLoaded', (event) => {
    const codeReader = new ZXing.BrowserQRCodeReader();
    const fileInput = document.getElementById('fileInput');

    codeReader.getVideoInputDevices().then((videoInputDevices) => {
        if (videoInputDevices.length > 0) {
            const selectedDeviceId = videoInputDevices[0].deviceId;

            codeReader.decodeFromVideoDevice(selectedDeviceId, 'preview', (result, err) => {
                if (result) {
                    console.log('QR Content: ', result.text);
                    processQRContent(result.text);
                }

                if (err && !(err instanceof ZXing.NotFoundException)) {
                    console.error('Error: ', err);
                }
            });
        } else {
            console.error('No video input devices found.');
        }
    }).catch((err) => {
        console.error('Error getting video input devices: ', err);
    });

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            fetch('/upload_qr', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.qr_data) {
                    processQRContent(data.qr_data);
                } else {
                    alert('Failed to upload QR code');
                }
            })
            .catch(error => {
                console.error('Error: ', error);
            });
        }
    });
});

function processQRContent(content) {
    fetch('/process_qr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ qr_data: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.uid) {
            alert('Payment made by user: ' + data.uid);
            document.getElementById('balance').innerText = data.balance;
        } else {
            alert('Invalid or expired QR code');
        }
    })
    .catch(error => {
        console.error('Error: ', error);
    });
}

function generateQRCode(userId) {
    fetch(`/generate_qr/${userId}`)
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.getElementById('downloadLink');
        a.style.display = 'block';
        a.href = url;
        a.download = 'qr_code.png';
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('Error generating QR code: ', error);
    });
}

function decodeQRCodeFromFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const codeReader = new ZXing.BrowserQRCodeReader();
                codeReader.decodeFromImage(img).then((result) => {
                    console.log('QR Content from file: ', result.text);
                    processQRContent(result.text);
                }).catch((err) => {
                    console.error('Error decoding QR from file: ', err);
                });
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}
