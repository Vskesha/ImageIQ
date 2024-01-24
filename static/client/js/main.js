const BASE_URL = window.location.origin;


function updatePageWithUserImages(imagesData, accessToken) {
    const imagesContainer = document.getElementById('userImagesContainer');
    imagesContainer.innerHTML = '';

    if (Array.isArray(imagesData.items) && imagesData.items.length > 0) {
        imagesData.items.forEach(image => {
            const imageContainer = document.createElement('div');
            const imageElement = document.createElement('img');
            imageElement.src = image.link;
            imageElement.alt = image.description;

            const descriptionElement = document.createElement('p');
            descriptionElement.innerText = `Description: ${image.description}`;

            const tagsElement = document.createElement('p');
            tagsElement.innerText = 'Tags: ';

            if (Array.isArray(image.tags) && image.tags.length > 0) {
                image.tags.forEach(tag => {
                    const tagSpan = document.createElement('span');
                    tagSpan.innerText = tag.name;
                    tagsElement.appendChild(tagSpan);
                });
            } else {
                tagsElement.innerText += 'No tags';
            }

            const deleteButton = document.createElement('button');
            deleteButton.innerText = '❌';

            deleteButton.addEventListener('click', async () => {
                try {
                    const deleteResponse = await fetch(`${BASE_URL}/api/images/${image.id}`, {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${accessToken}`,
                        },
                    });

                    if (deleteResponse.ok) {
                        imageContainer.remove();
                    } else {
                        const deleteError = await deleteResponse.json();
                        console.error('Error deleting image:', deleteError);
                    }
                } catch (deleteError) {
                    console.error('Error deleting image:', deleteError);
                }
            });

            imageContainer.appendChild(deleteButton);
            imageContainer.appendChild(imageElement);
            imageContainer.appendChild(descriptionElement);
            imageContainer.appendChild(tagsElement);


            imagesContainer.appendChild(imageContainer);
        });
    } else {
        const noImagesMessage = document.createTextNode('No images found.');
        imagesContainer.appendChild(noImagesMessage);
    }
}


const accessToken = localStorage.getItem('accessToken');

document.addEventListener('DOMContentLoaded', async function () {
    try {
        if (!accessToken) {
            console.error('Access token not available. Please log in.');
            return;
        }

        const response = await fetch(`${BASE_URL}/api/images/by_user`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        });

        if (response.ok) {
            const imagesData = await response.json();
            console.log('User images:', imagesData);
            updatePageWithUserImages(imagesData, accessToken);
        } else {
            const error = await response.json();
            console.error('Error fetching user images:', error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
});


