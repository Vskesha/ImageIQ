const BASE_URL = window.location.origin;
const form = document.forms[0];

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
        const response = await fetch(`${BASE_URL}/api/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: form.username.value,
                email: form.email.value,
                password: form.password.value,
                confirm_password: form.confirm_password.value,
            }),
        });

        console.log(response.status, response.statusText);

        if (response.status === 201) {
            const result = await response.json();
            localStorage.setItem('accessToken', result.access_token);
            localStorage.setItem('refreshToken', result.refresh_token);
//            window.location = '/src/services/templates/email_confirm.html';
            const token = result.access_token;

            // Здійснити перехід за адресою `/api/auth/confirmed_email/${token}`
            window.location = `${BASE_URL}/api/auth/confirmed_email/${token}`;
        } else {
            const errorResult = await response.json();
            console.error('Registration failed:', errorResult.detail);
        }
    } catch (error) {
        console.error('An error occurred:', error);
    }
});



//let currentUrl = window.location.href;
//if (currentUrl.includes("/email-confirm/done")) {
//    window.location.href = `${BASE_URL}/static/client/signin.html`;
//}
