// define contants for various variables
const logPasswordField = document.querySelector("#id_password");
const logPassField = document.querySelector("#id_pass");
const signPasswordField = document.querySelector("#id_password1");
const confirmSignPasswordField = document.querySelector("#id_password2");
const signupForm = document.querySelector('signupForm'); // replace 'form' with the ID or class of your form element

// // Function to toggle password visibility
function togglePasswordVisibility(formType, toggleIcon, passPosition = "") {
    if (formType == "login") {
        if (logPasswordField.type == "text" || logPassField.type == "text") {
            logPasswordField.type = "password";
            logPassField.type = "password";
            toggleIcon.innerHTML = '<i class="fa-regular fa-eye fa-lg"></i>';
        } else {
            logPasswordField.type = "text";
            logPassField.type = "text";
            toggleIcon.innerHTML = '<i class="fa-regular fa-eye-slash fa-lg"></i>';
        }
    } else if (formType == "signup") {
        if (passPosition == "theFirst") {
            if (signPasswordField.type == "text") {
                signPasswordField.type = "password";
                toggleIcon.innerHTML = '<i class="fa-regular fa-eye fa-lg"></i>';
            }
            else {
                signPasswordField.type = "text";
                toggleIcon.innerHTML = '<i class="fa-regular fa-eye-slash fa-lg"></i>';
            }
        }
        else if (passPosition == "theSecond") {
            if (confirmSignPasswordField.type == "text") {
                confirmSignPasswordField.type = "password";
                toggleIcon.innerHTML = '<i class="fa-regular fa-eye fa-lg"></i>';
            }
            else {
                confirmSignPasswordField.type = "text";
                toggleIcon.innerHTML = '<i class="fa-regular fa-eye-slash fa-lg"></i>';
            }

        }
    }
}

function showMessage(message, alertType) {
    Swal.fire({
        icon: alertType,
        title: message,
        showConfirmButton: true,
    })

}
