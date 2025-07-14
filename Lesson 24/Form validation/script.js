function validate(e){
    e.preventDefault();
    const email=document.getElementById("email").value;
    const pass = document.getElementById("password").value;
    const age = document.getElementById("age").value;
    const msgbox = document.getElementById("message").value;
    var message="";
    if (email===""){
        message="enter an email";
        msgbox.style.color="red"
    }
}