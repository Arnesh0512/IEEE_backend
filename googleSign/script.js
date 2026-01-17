// script.js

function handleGoogleLogin(response) {
    const googleIdToken = response.credential;

    fetch("http://localhost:8000/auth/user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            token: googleIdToken
        })
    })
    .then(res => {
        if (!res.ok) {
            throw new Error("Authentication failed");
        }
        return res.json();
    })
    .then(data => {
        localStorage.setItem("access_token", data.access_token);
        window.location.href = "home.html";
    })
    .catch(err => {
        console.error(err);
        alert("Google sign-in failed");
    });
}
