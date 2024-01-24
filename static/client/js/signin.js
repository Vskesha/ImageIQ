const BASE_URL = window.location.origin;
const form = document.forms[0];

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const response = await fetch(`${BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: form.username.value,
                password: form.password.value,
            }),
        });

        console.log(response.status, response.statusText);

        if (response.status === 200) {
            const result = await response.json();
            localStorage.setItem('accessToken', result.access_token);
            localStorage.setItem('refreshToken', result.refresh_token);
            localStorage.setItem('username', result.username);
            localStorage.setItem('avatar', result.avatar);
            window.location = 'main.html';
            form.username.value = '';
            form.password.value = '';
        }
    } catch (error) {
        console.error('An error occurred:', error);
    }
});



let currentUrl = window.location.href;
if (currentUrl.includes("/reset-password/confirm/")) {
    window.location.href = `${BASE_URL}/static/client/signin.html`;
}

