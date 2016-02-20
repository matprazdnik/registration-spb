function pressed(u, f) {
  var code = event.keyCode;
  if (code == 13) {
    var xhttp = new XMLHttpRequest();
    var field = document.getElementById("u_" + u + "_" + f);
    var val = field.value;
    if (f == 'work') {
      var ok = false;
      if (val.length == 7) {
        ok = true;
        for (var i = 0; i < 7; i++) {
          if (i == 4) {
            if (val[i] != '-') {
              ok = false;
            }
          } else {
            if (!(val[i] >= '0' && val[i] <= '9')) {
              ok = false;
            }
          }
        }
        var ch1 = ((val[0] - '0') + (val[1] - '0') + (val[2] - '0') + (val[3] - '0')) % 10;
        var ch2 = ((val[0] - '0') + 3 * (val[1] - '0') + 7 * (val[2] - '0') + 9 * (val[3] - '0')) % 10;
        if (ch1 != val[5] - '0' || ch2 != val[6] - '0') {
          ok = false;
        }
      }
      if (!ok) {
        alert('Некорректный код бланка!');
        return;
      }
    }
    field.disabled = true;
    xhttp.open("GET", "/matprazdnik/admin/do_edit?" + "id=" + u + "&f=" + f + "&v=" + val, true);
    xhttp.send();
    xhttp.onreadystatechange = function(e) {
      if (xhttp.readyState == 4) {
        field.disabled = false;
        a = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6'];
        f1 = '';
        for (var i = 0; i + 1 < a.length; i++) {
          if (a[i] == f) {
            f1 = a[i + 1];
          }
        }
        var sum = 0;
        for (var i = 0; i < a.length; i++) {
          sum += Number(document.getElementById("u_" + u + "_" + a[i]).value);
        }
        document.getElementById("u_" + u + "_" + "res").value = sum;
        if (f1 != '') {
          document.getElementById("u_" + u + "_" + f1).focus();
          document.getElementById("u_" + u + "_" + f1).select();
        }
      }
    };
  }
}
