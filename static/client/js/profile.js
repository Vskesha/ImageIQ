document.addEventListener('DOMContentLoaded', function () {
    const storedUserData = localStorage.getItem('userData');


    if (storedUserData) {
        const userData = JSON.parse(storedUserData);
        let createdAt = new Date(userData.created_at);
        let formattedDate = createdAt.toISOString().split('T')[0];

        document.getElementById('username').innerText = `Name: ${userData.username}`;
        document.getElementById('email').innerText = `Email: ${userData.email}`;
        document.getElementById('avatar_profile').src = userData.avatar;
        document.getElementById('comments_count').innerText = `Comments: ${userData.comments_count}`;
        document.getElementById('created_at').innerText = `Profile created: ${formattedDate}`;
        document.getElementById('images_count').innerText = `Images: ${userData.images_count}`;
    } else {
        console.error('User data not found in local storage');
    }
});
