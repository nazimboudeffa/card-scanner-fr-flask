const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureButton = document.getElementById('capture');
const result = document.getElementById('result');
const hashType = document.getElementById('hash_type');
const hashSize = document.getElementById('hash_size');

navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => video.srcObject = stream)
  .catch(err => console.error("Erreur d'accès à la caméra :", err));

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

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            result.textContent = `❌ Erreur: ${errorData.error || 'Erreur serveur'}`;
            console.error("Erreur serveur", response.status, errorData);
        } else {
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
                data.closest_matches.forEach((match, index) => {
                    html += `${index + 1}. ${match.name} (distance: ${match.distance})<br>`;
                });
            }
            
            result.innerHTML = html;
        }
    }, 'image/jpeg');
});