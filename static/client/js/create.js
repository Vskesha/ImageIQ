const BASE_URL = window.location.origin;

async function uploadImage() {
    try {
        const accessToken = localStorage.getItem('accessToken');

        if (!accessToken) {
            console.error('Access token not available. Please log in.');
            return;
        }

        const descriptionValue = document.getElementById('description').value;
        const tagsValue = document.getElementById('tags').value;

        const response = await fetch(`${BASE_URL}/api/images/?description=${encodeURIComponent(descriptionValue)}&tags=${encodeURIComponent(tagsValue)}`, {
            method: 'POST',
            body: new FormData(document.getElementById('imageForm')),
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Image created:', result);
            window.location.href = 'main.html';
        } else {
            const error = await response.json();
            console.error('Error creating image:', error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}


const closeModalButton = document.getElementById('closeModalButton');
const imageForm = document.getElementById('imageForm');
closeModalButton.addEventListener('click', function() {

    imageForm.style.display = 'none';})


