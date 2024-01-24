const BASE_URL = window.location.origin;


function updatePageWithUserImages(imagesData, accessToken) {
    const imagesContainer = document.getElementById('userImagesContainer');
    imagesContainer.innerHTML = '';

    if (Array.isArray(imagesData.items) && imagesData.items.length > 0) {
        imagesData.items.forEach(image => {
            const imageContainer = document.createElement('div');
            imageContainer.classList.add('image-container');
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
            deleteButton.innerText = '\u2716';

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
            updatePageWithUserImages(imagesData, accessToken);
        } else {
            const error = await response.json();
            console.error('Error fetching user images:', error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
});


document.addEventListener('DOMContentLoaded', async function () {
    const profileLink = document.getElementById('profile-link');
    const accessToken = localStorage.getItem('accessToken');
    profileLink.addEventListener('click', async function (event) {
        event.preventDefault();
        try {

            const response = await fetch(`${BASE_URL}/api/users/me`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });
            if (response.ok) {
                const userData = await response.json();
                console.log('Response data:', userData);
                localStorage.setItem('userData', JSON.stringify(userData));
                window.location = 'profile_template.html';
            } else {
                console.error('Request failed:', response.statusText);
            }
        } catch (error) {
            console.error('Error during fetch:', error);
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const username = localStorage.getItem('username');
    const avatar = localStorage.getItem('avatar');
    document.getElementById('username').innerText = `${username}`;
    document.getElementById('avatar').src = avatar;

});


document.getElementById('searchButton').addEventListener('click', function() {
    const tag_name = document.getElementById('tagInput').value;
    if (!tag_name) {
        alert('Please enter a tag name');
        return;
    }
     const access_token = localStorage.getItem('accessToken');
    fetch(`${BASE_URL}/api/images/search_bytag/${tag_name}`, {
        headers: {
            'Authorization': `Bearer ${access_token}`
        }
    })
        .then(response => response.json())
        .then(data => {
            displayModalContent(data);
        })
        .catch(error => console.error('Error:', error));
});


const searchLink = document.getElementById('searchLink');
const tagInput = document.getElementById('tagInput');
const searchButton = document.getElementById('searchButton');
const closeModalButton = document.getElementById('closeModalButton');
const linkHide = document.getElementById('link-hide');


function displayModalContent(data) {
    console.log(data);
    modalContent.innerHTML = '';
    const modal = document.getElementById('myModal');
    if (data && data.length > 0) {
        const item = data[0];
        const createdAt = new Date(item.created_at);
        const formDate = createdAt.toISOString().split('T')[0];
        const contentHTML = `
            <h2>${item.description}</h2>
            <p>Created at: ${formDate}</p>
            <p>Photo: <a href="${item.link}" target="_blank"><img src="${item.link}" alt="Image"></a></p> `;
        modalContent.innerHTML = contentHTML;
        modal.style.display = 'block';
    } else {
        alert('No items found.');
        modal.style.display = 'none';
        linkHide.style.display = 'none';
        searchLink.style.display = 'block';
    }


}


function closeModal() {
    const modal = document.getElementById('myModal');
    modal.style.display = 'none';
}



searchLink.addEventListener('click', function() {
    linkHide.style.display = 'inline-block';
    searchLink.style.display = 'none';
    tagInput.focus();

    timeoutId = setTimeout(function() {
        linkHide.style.display = 'none';
        searchLink.style.display = 'inline-block';
        tagInput.value = '';  // Очистка значення поля вводу
    }, 5000);
});


tagInput.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        tagInput.style.display = 'none';
        searchButton.style.display = 'none';
        searchLink.style.display = 'inline-block';
        tagInput.value = '';
        clearTimeout(timeoutId);
    }
});


closeModalButton.addEventListener('click', function() {
    tagInput.value = '';
    searchLink.style.display = 'inline-block';
    linkHide.style.display = 'none';
    closeModal();
    clearTimeout(timeoutId);
});