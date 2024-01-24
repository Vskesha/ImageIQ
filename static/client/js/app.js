token = localStorage.getItem('accessToken')

const BASE_URL = window.location.origin;



const logoutButton = document.getElementById('logoutButton');

logoutButton.addEventListener('click', async () => {
    try {
        const accessToken = localStorage.getItem('accessToken');
        const response = await fetch(`${BASE_URL}/api/auth/logout`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        });

        console.log(response.status, response.statusText);

        if (response.status === 205) {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            window.location = '/static/client/signin.html';
        }
    } catch (error) {
        console.error('An error occurred:', error);
    }
});


//
//
//async function uploadImage() {
//        const formData = new FormData(document.getElementById('imageForm'));
//
//        try {
//        const accessToken = localStorage.getItem('accessToken');  // Replace with your actual authentication token
//
//        const response = await fetch(`${BASE_URL}/api/images/`, {
//            method: 'POST',
//            body: formData,
//            headers: {
//                'Authorization': `Bearer ${accessToken}`,  // Include the token in the Authorization header
//            },
//        });
//
//            if (response.ok) {
//                const result = await response.json();
//                console.log('Image created:', result);
//
//                // Assuming 'result' contains the image URL, you can display it on the page
//                const imageContainer = document.getElementById('imageContainer');
//                const imageElement = document.createElement('img');
//                imageElement.src = result.link;  // Assuming 'link' is the property containing the image URL
//                imageElement.alt = result.description;  // Assuming 'description' is the property containing the image description
//                imageContainer.appendChild(imageElement);
//
//                // You can also display other information about the image
//                const descriptionContainer = document.getElementById('descriptionContainer');
//                const descriptionText = document.createTextNode('Description: ' + result.description);
//                descriptionContainer.appendChild(descriptionText);
//
//                // Add any other details you want to display on the page
//
//            } else {
//                const error = await response.json();
//                console.error('Error creating image:', error);
//                // Handle the error, e.g., display an error message to the user.
//            }
//        } catch (error) {
//            console.error('Error:', error);
//        }
//    }

// async function uploadImage() {
//        const formData = new FormData(document.getElementById('imageForm'));
//
//        try {
//            const accessToken = localStorage.getItem('accessToken');
//
//            if (!accessToken) {
//                console.error('Access token not available. Please log in.');
//                // You may want to redirect the user to the login page or display an error message
//                return;
//            }
//
//            const response = await fetch(`${BASE_URL}/api/images/`, {
//                method: 'POST',
//                body: formData,
//                headers: {
//                    'Authorization': `Bearer ${accessToken}`,
//                },
//            });
//
//            if (response.ok) {
//                const result = await response.json();
//                console.log('Image created:', result);
//
//                // Redirect to another page with query parameters
//                window.location.href = `/static/client/index.html?imageId=${result.id}&imageUrl=${result.link}&imageDescription=${result.description}`;
//            } else {
//                const error = await response.json();
//                console.error('Error creating image:', error);
//                // Handle the error, e.g., display an error message to the user.
//            }
//        } catch (error) {
//            console.error('Error:', error);
//        }
//    }



