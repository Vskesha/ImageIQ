token = localStorage.getItem('accessToken')





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
