// Handling light/dark mode
const body = document.querySelector('body'),
    sidebar = body.querySelector('nav'),
    toggle = body.querySelector(".toggle"),
    modeSwitch = body.querySelector(".toggle-switch"),
    modeText = body.querySelector(".mode-text");

toggle.addEventListener("click", () => {
    sidebar.classList.toggle("close");
})

// Select the theme preference from localStorage
const currentTheme = localStorage.getItem("theme");

// If the current theme in localStorage is "dark"...
if (currentTheme == "dark") {
    // ...then use the .dark-theme class
    body.classList.toggle("dark");
}

modeSwitch.addEventListener("click", () => {
    body.classList.toggle("dark");

    // Let's say the theme is equal to light
    let theme = "light";

    // If the body contains the .dark-theme class...
    if (body.classList.contains("dark")) {
        // ...then let's make the theme dark
        theme = "dark";
        modeText.innerText = "Light mode";
    }
    else {
        modeText.innerText = "Dark mode";
    }

    // Then save the choice in localStorage
    localStorage.setItem("theme", theme);
});

// Handling the webcam capturing of images
let canvas = document.querySelector("#canvas");
let context = canvas.getContext("2d");
let video = document.querySelector("#video");

if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
        video.srcObject = stream;
        video.play();
    });
}

document.getElementById("snap").addEventListener("click", () => {
    context.drawImage(video, 0, 0, 28, 28);

    $('#result').text('  Predicting...');
    var img = canvas.toDataURL('image/png');

    $.ajax({
        type: "POST",
        url: "https://dlwebapp-devyn.herokuapp.com/predict",
        data: img,
        success: function (resp) {
            if (resp['status'] == 'Uploaded') {
                // display success message if captured successfully
                $('.alert > .msg').text(`Successfully captured.`);
                $('.alert').addClass("show");
                $('.alert').removeClass("hide");
                $('.alert').addClass("showAlert");
                $('.alert').css({ "background": "#b7e4c7", "border-left": "8px solid #52b788" });
                $('.alert > .notif-icon').removeClass("fas fa-exclamation-circle")
                $('.alert > .notif-icon').addClass("far fa-smile")
                $('.alert > .notif-icon').css({ "position": "absolute", "left": "20px", "top": "50%", "transform": "translateY(-50%)", "color": "#40916c", "font-size": "30px" })
                $('.alert > .icon').css({ "color": "#40916c" });
                $('.alert > .msg').css({ "color": "#40916c" });
                $('.alert > .close-btn').css({ "background": "#76c893" });
                $('.alert > .close-btn > .fas').css({ "color": "#2d6a4f" });
                setTimeout(function () {
                    $('.alert').removeClass("show");
                    $('.alert').addClass("hide");
                }, 3000);
                // showing the prediction
                $('.prediction > .msg').text(`Our model predicted '${resp['prediction']}'.`);
                $('.prediction > .fas').addClass("fa-check-circle");
                setTimeout(function () {
                    $('.prediction > .msg').empty();
                    $('.prediction > .fas').removeClass("fa-check-circle");
                }, 5000);
            }
            else {
                $('.alert > .msg').text(`An error occurred while capturing your image.`);
                $('.alert').addClass("show");
                $('.alert').removeClass("hide");
                $('.alert').addClass("showAlert");
                setTimeout(function () {
                    $('.alert').removeClass("show");
                    $('.alert').addClass("hide");
                }, 3000);
            }

        }
    });
});

// close notification
$('.close-btn').click(function () {
    $('.alert').removeClass("show");
    $('.alert').addClass("hide");
});

// Handles error when uploading image files
function handleErrors(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}

// Handles the uploading of image files
const upload = document.querySelector("#upload"),
    fileInput = document.querySelector(".file-input")

upload.addEventListener("click", () => {
    fileInput.click();
});

fileInput.onchange = ({ target }) => {
    let file = target.files[0];
    if (file) {
        let fileName = file.name;
        if (fileName.length >= 12) {
            let splitName = fileName.split('.');
            fileName = splitName[0].substring(0, 13) + "... ." + splitName[1];
        }
        let formData = new FormData();
        formData.append("photo", file);
        fetch('https://dlwebapp-devyn.herokuapp.com/upload', { method: "POST", body: formData })
        .then(handleErrors)
        .then(response => response.json())
        .then(json => {
            console.log(json);
            if(json['status'] == 'Uploaded'){
                $('.alert > .msg').text(`Image successfully uploaded.`);
                $('.alert').addClass("show");
                $('.alert').removeClass("hide");
                $('.alert').addClass("showAlert");
                $('.alert').css({ "background": "#b7e4c7", "border-left": "8px solid #52b788" });
                $('.alert > .notif-icon').removeClass("fas fa-exclamation-circle")
                $('.alert > .notif-icon').addClass("far fa-smile")
                $('.alert > .notif-icon').css({ "position": "absolute", "left": "20px", "top": "50%", "transform": "translateY(-50%)", "color": "#40916c", "font-size": "30px" })
                $('.alert > .icon').css({ "color": "#40916c" });
                $('.alert > .msg').css({ "color": "#40916c" });
                $('.alert > .close-btn').css({ "background": "#76c893" });
                $('.alert > .close-btn > .fas').css({ "color": "#2d6a4f" });
                setTimeout(function () {
                    $('.alert').removeClass("show");
                    $('.alert').addClass("hide");
                }, 3000);
                // showing the prediction
                $('.prediction > .msg').text(`Our model predicted '${json['prediction']}'.`);
                $('.prediction > .fas').addClass("fa-check-circle");
                setTimeout(function () {
                    $('.prediction > .msg').empty();
                    $('.prediction > .fas').removeClass("fa-check-circle");
                }, 5000);
            }
            else {
                $('.alert > .msg').text(`An error occurred while capturing your image.`);
                $('.alert').addClass("show");
                $('.alert').removeClass("hide");
                $('.alert').addClass("showAlert");
                setTimeout(function () {
                    $('.alert').removeClass("show");
                    $('.alert').addClass("hide");
                }, 3000);
            }
            
        })
        .catch((error) => {
            console.log(error)
            $('.alert > .msg').text(`A server error occurred while capturing your image.`);
            $('.alert').addClass("show");
            $('.alert').removeClass("hide");
            $('.alert').addClass("showAlert");
            setTimeout(function () {
                $('.alert').removeClass("show");
                $('.alert').addClass("hide");
            }, 3000);
        });
    }
}

// Search filename
function search() {
    // Declare variables
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("history");
    tr = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[1];
        if (td) {
            txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}

// Clear all button
$('.clear-all').click(function () {
    $('.alert').removeClass("show");
    $('.alert').addClass("hide");
});