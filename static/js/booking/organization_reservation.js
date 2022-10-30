var list_of_reservation = [];
var form = document.getElementById("submit-form");
var result_json = document.getElementById("result_json");
var submit_reservation = document.getElementById("submit-reservation");

function remove_reservation(value) {
  var i = 0;
  while (i < list_of_reservation.length) {
    if (list_of_reservation[i].order_data === value.order_data
        && list_of_reservation[i].apartment_id === value.apartment_id) {
      list_of_reservation.splice(i, 1);
    } else {
      ++i;
    }
  }
}

function disable_submit_button() {
    if (list_of_reservation.length) {
        submit_reservation.className = "btn btn-primary";
        submit_reservation.removeAttribute("aria-disabled");
    }
    else {
        submit_reservation.className = "btn btn-primary disabled";
        submit_reservation.setAttribute('aria-disabled', true);
    }
}

submit_reservation.addEventListener("click", function () {
    result_json.value = JSON.stringify(list_of_reservation)
    form.submit();
});



window.onclick = e => {
    var current_booking = {
        'order_data': e.target.getAttribute("order_data"),
        'apartment_id': e.target.getAttribute("apartment_id")
    };
    if (e.target.className == "badge badge-info"){
        e.target.className = "badge badge-success";
        list_of_reservation.push(current_booking);
        disable_submit_button();
    }
    else if ( e.target.className == "badge badge-success") {
         e.target.className = "badge badge-info";
         remove_reservation(current_booking);
         disable_submit_button();
    }
    //console.log(list_of_reservation)
}
