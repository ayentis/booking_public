function hello() {
    alert(this.innerHTML+"hello");
}

const element = document.getElementById("buttonAbout");
element.onclick = hello