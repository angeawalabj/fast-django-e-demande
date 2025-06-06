document.addEventListener("DOMContentLoaded", function() {
    // Gestion des boutons
    const buttons = document.querySelectorAll("button");
    buttons.forEach(button => {
        button.dataset.originalText = button.textContent;
        button.addEventListener("mouseover", function() {
            this.style.backgroundColor = "#00509e";
        });
        button.addEventListener("mouseout", function() {
            this.style.backgroundColor = "#0066b6";
        });
        button.addEventListener("click", function() {
            this.disabled = true;
            this.textContent = "Envoi...";
            setTimeout(() => {
                this.disabled = false;
                this.textContent = this.dataset.originalText;
            }, 2000);
        });
    });

    // Validation du formulaire de connexion
    const loginForm = document.querySelector("#loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            const email = document.getElementById("email");
            const password = document.getElementById("password");
            let valid = true;

            // Reset feedback
            [email, password].forEach(input => {
                input.classList.remove("is-invalid");
                input.nextElementSibling.textContent = "";
            });

            // Validate email
            if (!email.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                email.classList.add("is-invalid");
                email.nextElementSibling.textContent = "Veuillez entrer un email valide";
                valid = false;
            }

            // Validate password
            if (password.value.length < 6) {
                password.classList.add("is-invalid");
                password.nextElementSibling.textContent = "Le mot de passe doit contenir au moins 6 caractères";
                valid = false;
            }

            if (valid) {
                const formData = new FormData(this);
                try {
                    const response = await fetch("{% url 'connecter' %}", {
                        method: "POST",
                        body: formData,
                        headers: { "X-CSRFToken": "{{ csrf_token }}" }
                    });
                    if (response.ok) {
                        window.location.href = "{% url 'dashboard' %}";
                    } else {
                        const data = await response.json();
                        alert(data.message || "Erreur de connexion");
                    }
                } catch (error) {
                    alert("Erreur lors de la connexion");
                }
            }
        });
    }

    // Validation du formulaire d'inscription
    const registerForm = document.querySelector("#registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            const email = document.getElementById("email");
            const password = document.getElementById("password");
            const repassword = document.getElementById("repassword");
            const matricule = document.getElementById("matricule");
            let valid = true;

            // Reset feedback
            [email, password, repassword, matricule].forEach(input => {
                input.classList.remove("is-invalid");
                input.nextElementSibling.textContent = "";
            });

            // Validate email
            if (!email.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                email.classList.add("is-invalid");
                email.nextElementSibling.textContent = "Veuillez entrer un email valide";
                valid = false;
            }

            // Validate password
            if (password.value.length < 6) {
                password.classList.add("is-invalid");
                password.nextElementSibling.textContent = "Le mot de passe doit contenir au moins 6 caractères";
                valid = false;
            }

            // Validate password confirmation
            if (password.value !== repassword.value) {
                repassword.classList.add("is-invalid");
                repassword.nextElementSibling.textContent = "Les mots de passe ne correspondent pas";
                valid = false;
            }

            // Validate matricule
            if (matricule.value.length < 3) {
                matricule.classList.add("is-invalid");
                matricule.nextElementSibling.textContent = "Le matricule doit contenir au moins 3 caractères";
                valid = false;
            }

            if (valid) {
                const formData = new FormData(this);
                try {
                    const response = await fetch("{% url 'inscription' %}", {
                        method: "POST",
                        body: formData,
                        headers: { "X-CSRFToken": "{{ csrf_token }}" }
                    });
                    if (response.ok) {
                        window.location.href = "{% url 'connecter' %}";
                    } else {
                        const data = await response.json();
                        alert(data.message || "Erreur lors de l'inscription");
                    }
                } catch (error) {
                    alert("Erreur lors de l'inscription");
                }
            }
        });
    }

    // Validation du formulaire de demande
    const requestForm = document.querySelector("#requestForm");
    if (requestForm) {
        requestForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            const typeDocument = document.getElementById("type_document");
            const filiere = document.getElementById("filiere");
            const obtention = document.getElementById("obtention");
            let valid = true;

            // Reset feedback
            [typeDocument, filiere, obtention].forEach(input => {
                input.classList.remove("is-invalid");
                input.nextElementSibling.textContent = "";
            });

            // Validate type_document
            if (!typeDocument.value) {
                typeDocument.classList.add("is-invalid");
                typeDocument.nextElementSibling.textContent = "Veuillez choisir un type de document";
                valid = false;
            }

            // Validate filiere
            if (!filiere.value.match(/^[A-Za-z0-9]{2,}$/)) {
                filiere.classList.add("is-invalid");
                filiere.nextElementSibling.textContent = "Veuillez entrer une filière valide (ex. MI2, PC3)";
                valid = false;
            }

            // Validate obtention
            if (!obtention.value.match(/^\d{4}-\d{4}$/)) {
                obtention.classList.add("is-invalid");
                obtention.nextElementSibling.textContent = "Veuillez entrer une année valide (ex. 2022-2023)";
                valid = false;
            }

            if (valid) {
                const formData = new FormData(this);
                try {
                    const response = await fetch("{% url 'demande' %}", {
                        method: "POST",
                        body: formData,
                        headers: { "X-CSRFToken": "{{ csrf_token }}" }
                    });
                    if (response.ok) {
                        window.location.href = "{% url 'dashboard' %}";
                    } else {
                        const data = await response.json();
                        alert(data.message || "Erreur lors de l'envoi de la demande");
                    }
                } catch (error) {
                    alert("Erreur lors de l'envoi de la demande");
                }
            }
        });
    }

    // Validation du formulaire de contact
    const contactForm = document.querySelector("#contactForm");
    if (contactForm) {
        contactForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            const nom = document.getElementById("nom");
            const email = document.getElementById("email");
            const sujet = document.getElementById("sujet");
            const message = document.getElementById("message");
            let valid = true;

            // Reset feedback
            [nom, email, sujet, message].forEach(input => {
                input.classList.remove("is-invalid");
                input.nextElementSibling.textContent = "";
            });

            // Validate nom
            if (!nom.value) {
                nom.classList.add("is-invalid");
                nom.nextElementSibling.textContent = "Veuillez entrer votre nom";
                valid = false;
            }

            // Validate email
            if (!email.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                email.classList.add("is-invalid");
                email.nextElementSibling.textContent = "Veuillez entrer un email valide";
                valid = false;
            }

            // Validate sujet
            if (!sujet.value) {
                sujet.classList.add("is-invalid");
                sujet.nextElementSibling.textContent = "Veuillez entrer un sujet";
                valid = false;
            }

            // Validate message
            if (!message.value) {
                message.classList.add("is-invalid");
                message.nextElementSibling.textContent = "Veuillez entrer un message";
                valid = false;
            }

            if (valid) {
                const formData = new FormData(this);
                try {
                    const response = await fetch("{% url 'contact' %}", {
                        method: "POST",
                        body: formData,
                        headers: { "X-CSRFToken": "{{ csrf_token }}" }
                    });
                    if (response.ok) {
                        window.location.href = "{% url 'dashboard' %}";
                    } else {
                        const data = await response.json();
                        alert(data.message || "Erreur lors de l'envoi du message");
                    }
                } catch (error) {
                    alert("Erreur lors de l'envoi du message");
                }
            }
        });
    }

    // Validation du formulaire de récupération
    const recoverForm = document.querySelector("#recoverForm");
    if (recoverForm) {
        recoverForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            const email = document.getElementById("email");
            email.classList.remove("is-invalid");
            email.nextElementSibling.textContent = "";

            if (!email.value.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                email.classList.add("is-invalid");
                email.nextElementSibling.textContent = "Veuillez entrer un email valide";
                return;
            }

            const formData = new FormData(this);
            try {
                const response = await fetch("{% url 'recuperation' %}", {
                    method: "POST",
                    body: formData,
                    headers: { "X-CSRFToken": "{{ csrf_token }}" }
                });
                if (response.ok) {
                    window.location.href = "{% url 'connecter' %}";
                } else {
                    const data = await response.json();
                    alert(data.message || "Erreur lors de la récupération");
                }
            } catch (error) {
                alert("Erreur lors de la récupération");
            }
        });
    }
});