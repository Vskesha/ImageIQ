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


//const BASE_URL = window.location.origin;
//
//async function uploadImage() {
//    try {
//        const accessToken = localStorage.getItem('accessToken');
//
//        if (!accessToken) {
//            console.error('Access token not available. Please log in.');
//            return;
//        }
//
//        const formData = new FormData();
//        const description = document.getElementById('description').value;
//        const tags = document.getElementById('tags').value;
//        const fileInput = document.getElementById('file');
//
//        console.log('Description value:', description);
//        console.log('Tags value:', tags);
//
//        formData.append('description', description);
//        formData.append('tags', tags);
//        formData.append('file', fileInput.files[0]);
//
//        const response = await fetch(`${BASE_URL}/api/images/`, {
//            method: 'POST',
//            body: formData,
//            headers: {
//                'Authorization': `Bearer ${accessToken}`,
//            },
//        });
//
//        if (response.ok) {
//            const result = await response.json();
//            console.log('Image created:', result);
////            window.location.href = 'main.html';
//        } else {
//            const error = await response.json();
//            console.error('Error creating image:', error);
//        }
//    } catch (error) {
//        console.error('Error:', error);
//    }
//}

//async function uploadImage() {
//    const formData = new FormData(document.getElementById('imageForm'));
//
//    try {
//        const accessToken = localStorage.getItem('accessToken');
//
//        if (!accessToken) {
//            console.error('Access token not available. Please log in.');
//            return;
//        }
//        const descriptionValue = document.getElementById('description').value;
//        console.log(typeof descriptionValue);
//        console.log('Description value:', descriptionValue);
//        formData.set('description', descriptionValue);
//        formData.forEach((value, key) => {
//    console.log(`${key}: ${value}`);
//});
//
//
//        const response = await fetch(`${BASE_URL}/api/images/`, {
//            method: 'POST',
//            body: formData,
//            headers: {
//                'Authorization': `Bearer ${accessToken}`,
//            },
//        });
//
//        if (response.ok) {
//            const result = await response.json();
//            console.log('Image created:', result);
////            window.location.href = 'main.html';
//        } else {
//            const error = await response.json();
//            console.error('Error creating image:', error);
//        }
//    } catch (error) {
//        console.error('Error:', error);
//    }
//}
//
//async function uploadImage() {
//    try {
//        const accessToken = localStorage.getItem('accessToken');
//
//        if (!accessToken) {
//            console.error('Access token not available. Please log in.');
//            return;
//        }
//
//        // Отримуємо значення з поля description
//        const descriptionValue = document.getElementById('description').value;
//
//        // Лог для перевірки значення description
//        console.log('Description:', descriptionValue);
//
//        // Створюємо новий об'єкт FormData
//        const formData = new FormData(document.getElementById('imageForm'));
//
//        // Додаємо значення description до formData
//        formData.append('description', descriptionValue);
//
//        // Відправляємо запит на сервер
//        const response = await fetch(`${BASE_URL}/api/images/`, {
//            method: 'POST',
//            body: formData,
//            headers: {
//                'Authorization': `Bearer ${accessToken}`,
//            },
//        });
//
//        if (response.ok) {
//            const result = await response.json();
//            console.log('Image created:', result);
////            window.location.href = 'main.html';
//        } else {
//            const error = await response.json();
//            console.error('Error creating image:', error);
//        }
//    } catch (error) {
//        console.error('Error:', error);
//    }
//}
//async function uploadImage() {
//    const formData = new FormData(document.getElementById('imageForm'));
//
//    try {
//        const accessToken = localStorage.getItem('accessToken');
//
//        if (!accessToken) {
//            console.error('Access token not available. Please log in.');
//            return;
//        }
//
//        const response = await fetch(`${BASE_URL}/api/images/`, {
//            method: 'POST',
//            body: formData,
//            headers: {
//                'Authorization': `Bearer ${accessToken}`,
//            },
//        });
//
//        if (response.ok) {
//            const result = await response.json();
//            console.log('Image created:', result);
//            window.location.href = 'main.html';
//        } else {
//            const error = await response.json();
//            console.error('Error creating image:', error);
//        }
//    } catch (error) {
//        console.error('Error:', error);
//    }
//}
