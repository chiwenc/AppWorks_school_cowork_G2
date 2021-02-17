const signinForm = document.getElementById('signin_form');
const signupForm = document.getElementById('signup_form');

if (signinForm) {
    signinForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const data = $('form').serializeArray().reduce(function(obj, item) {
            obj[item.name] = item.value;
            return obj;
        }, {});

        $.post("/api/1.0/signin", {email: data.email, password: data.password}, function(data) {
            console.log(data);
            const localStorage = window.localStorage;
            localStorage.setItem('access_token', data.access_token);
            window.location.href = "/profile.html";
        }, "json");
    });
}

if (signupForm) {
    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const data = $('form').serializeArray().reduce(function(obj, item) {
            obj[item.name] = item.value;
            return obj;
        }, {});

        console.log(data);
        $.post("/api/1.0/signup", {name: data.name, email: data.email, password: data.password}, function(data) {
            const localStorage = window.localStorage;
            localStorage.setItem('access_token', data.access_token);
            window.location.href = "/profile.html";
        }, "json");
    });
}
