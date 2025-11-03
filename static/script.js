const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureButton = document.getElementById('capture');
const switchButton = document.getElementById('switch_camera');
const result = document.getElementById('result');
const hashType = document.getElementById('hash_type');
const hashSize = document.getElementById('hash_size');

let currentStream = null;
let currentFacing = 'environment'; // start with back camera for scanning

function updateSwitchLabel() {
    if (!switchButton) return;
    switchButton.textContent = currentFacing === 'user' ? 'Caméra: avant' : 'Caméra: arrière';
}

function stopStream() {
    if (currentStream) {
        for (const t of currentStream.getTracks()) {
            t.stop();
        }
        currentStream = null;
    }
}

async function pickDeviceId(preferred) {
    // Ensure permission so labels are available
    try {
        const tmp = await navigator.mediaDevices.getUserMedia({ video: true });
            for (const t of tmp.getTracks()) {
                t.stop();
            }
        } catch (error_) {
            console.warn('Permission or temporary camera access failed for label discovery:', error_);
    }
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videos = devices.filter(d => d.kind === 'videoinput');
    if (!videos.length) return null;

    // Try to find by label hints
    const target = videos.find(d => /back|rear|arrière|environment/i.test(d.label)) ||
                                 videos.find(d => /front|avant|user/i.test(d.label));

    if (preferred === 'user') {
        const front = videos.find(d => /front|avant|user/i.test(d.label));
        if (front) return front.deviceId;
    }
    if (preferred === 'environment') {
        const back = videos.find(d => /back|rear|arrière|environment/i.test(d.label));
        if (back) return back.deviceId;
    }
    return (target || videos[0]).deviceId;
}

async function startCamera(facing = 'environment') {
    currentFacing = facing;
    updateSwitchLabel();
    stopStream();
    const constraintsFacing = { video: { facingMode: { ideal: facing } } };
        try {
        const stream = await navigator.mediaDevices.getUserMedia(constraintsFacing);
        currentStream = stream;
        video.srcObject = stream;
        await video.play();
        return;
            } catch (error_) {
                console.warn('facingMode constraint failed; trying deviceId fallback…', error_);
                // Fallback to deviceId selection if facingMode not supported
        try {
            const deviceId = await pickDeviceId(facing);
            const stream = await navigator.mediaDevices.getUserMedia({ video: deviceId ? { deviceId: { exact: deviceId } } : true });
            currentStream = stream;
            video.srcObject = stream;
            await video.play();
            return;
            } catch (error_) {
                console.error("Erreur d'accès à la caméra :", error_);
            result.textContent = '❌ Erreur d\'accès à la caméra';
        }
    }
}

    // Initialize camera on load (top-level await in module)
    await startCamera(currentFacing);

// Toggle camera on button
if (switchButton) {
    switchButton.addEventListener('click', async () => {
        const next = currentFacing === 'user' ? 'environment' : 'user';
        await startCamera(next);
    });
}

captureButton.addEventListener('click', async () => {
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convertir le canvas en Blob
    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('image', blob, 'capture.jpg');
        formData.append('hash_type', hashType.value);
        formData.append('hash_size', hashSize.value);

        const response = await fetch('/compare', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            
            let html = '';
            
            if (data.exact_match) {
                html += '✅ <strong>Match exact trouvé!</strong><br>';
            } else if (data.total_matches > 0) {
                html += '🔍 <strong>Correspondances proches:</strong><br>';
            } else {
                html += '🆕 <strong>Aucune correspondance trouvée</strong><br>';
            }
            
            html += `Hash: ${data.hash}<br>`;
            html += `Type: ${data.hash_type} (size: ${data.hash_size})<br><br>`;
            
            if (data.closest_matches && data.closest_matches.length > 0) {
                html += '<strong>Meilleures correspondances:</strong><br>';
                for (const [index, match] of data.closest_matches.entries()) {
                    html += `${index + 1}. ${match.name} (distance: ${match.distance})<br>`;
                }
            }
            
            result.innerHTML = html;
        } else {
            const errorData = await response.json().catch(() => ({}));
            result.textContent = `❌ Erreur: ${errorData.error || 'Erreur serveur'}`;
            console.error("Erreur serveur", response.status, errorData);
        }
    }, 'image/jpeg');
});