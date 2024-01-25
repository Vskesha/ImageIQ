const BASE_URL = window.location.origin;


function updatePageWithUserImages(imagesData, accessToken) {
    const imagesContainer = document.getElementById('userImagesComments');
    imagesContainer.innerHTML = '';

    if (Array.isArray(imagesData.items) && imagesData.items.length > 0) {
        imagesData.items.forEach(image => {
            const imageContainer = document.createElement('div');
            imageContainer.classList.add('image-container');

            const deleteButton = document.createElement('button');
            deleteButton.classList.add('delete-button');
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

            const imageLink = document.createElement('a');
            imageLink.href = image.link;
            imageLink.target = '_blank';

            const imageElement = document.createElement('img');
            imageElement.src = image.link;
            imageElement.classList.add('image-comments')

            imageLink.appendChild(imageElement);

            const commentInput = document.createElement('textarea');
            commentInput.placeholder = 'Enter your comment...';

            const addCommentButton = document.createElement('button');
            addCommentButton.innerText = 'Add';
            addCommentButton.classList.add('add-comment');

            addCommentButton.addEventListener('click', () => {
                const commentText = commentInput.value;
                if (commentText.trim() !== '') {
                    addCommentToImage(image.id, commentText, accessToken);
                    commentInput.value = '';
                    commentsContainer.style.display = 'block';
                }
            });
            const commentsContainer = document.createElement('div');
            commentsContainer.id = `commentsContainer-${image.id}`;
            commentsContainer.classList.add('container-comment');


            imageContainer.appendChild(deleteButton);
            imageContainer.appendChild(imageLink);
            imageContainer.appendChild(commentsContainer);
            imageContainer.appendChild(commentInput);
            imageContainer.appendChild(addCommentButton);
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


async function addCommentToImage(imageId, commentText, accessToken) {
    try {
        const response = await fetch(`${BASE_URL}/api/comment/${imageId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                comment: commentText,
            }),
        });

        if (response.ok) {
            const commentData = await response.json();
            const commentsContainer = document.getElementById(`commentsContainer-${imageId}`);
            const commentElement = document.createElement('div');
            commentElement.classList.add('comment');
            const commentTextElement = document.createElement('p');
            commentTextElement.innerText = commentData.comment;
            commentElement.appendChild(commentTextElement);
            commentsContainer.appendChild(commentElement);
            console.log('Comment added:', commentData);
        } else {
            const error = await response.json();
            console.error('Error adding comment:', error);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}


function addComment(imageId) {
    const commentText = document.getElementById('commentInput').value;
    if (commentText.trim() === '') {
        alert('Введіть текст коментаря.');
        return;
    }

    addCommentToImage(imageId, commentText, accessToken);
    document.getElementById('commentInput').value = '';
}