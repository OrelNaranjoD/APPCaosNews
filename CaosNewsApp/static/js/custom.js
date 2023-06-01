/* ********* Obtener fecha actual ********* */
function getFecha(){
  const Month = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio",
    "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
  ];
  const Day = [
    "Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado",
  ];
  const date = new Date();

  document.getElementById("current_date").innerHTML = Day[date.getDay()] + " " + date.getDate() + " de " + Month[date.getMonth()] + " de " + date.getFullYear();
}


/* VALIDACIONES MUAJAJJA */
function validarFormulario() {
  console.log("validando formulario");
  // Validar que los campos obligatorios estén completos
  const nombre = document.getElementById("nombre").value.trim();
  const email = document.getElementById("email").value.trim();
  const telefono = document.getElementById("phone").value.trim();
  
  if (nombre === "" || email === "" || telefono === "") {
    alert("Por favor, complete todos los campos obligatorios.");
    return false;
  }




  // Validar el formato del correo electrónico
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    alert("Por favor, ingrese una dirección de correo electrónico válida.");
    return false;
  }

  // Validar el formato del número de teléfono
  const telefonoRegex = /^\d{9}$/;
  if (!telefonoRegex.test(telefono)) {
    alert("Por favor, ingrese un número de teléfono válido.");
    return false;
  }

  // Si todas las validaciones han pasado, se puede enviar el formulario
  return true;
}


//VALIDACIONES PARA EL LOGIN MUAJAJJA //

function validarEmail(email) {
	// Expresión regular para validar el formato del correo electrónico
	var re = /\S+@\S+\.\S+/;
	return re.test(email);
}

function validarlogin() {
	var email = document.getElementById("email").value;
	var password = document.getElementById("password").value;

	// Validar que el correo electrónico no esté vacío
	if (email == "") {
		alert("El campo de correo electrónico no puede estar vacío.");
		return false;
	}

	// Validar el formato del correo electrónico
	if (!validarEmail(email)) {
		alert("El correo electrónico ingresado no es válido.");
		return false;
	}

	// Validar que la contraseña no esté vacía
	if (password == "") {
		alert("El campo de contraseña no puede estar vacío.");
		return false;
	}

	// si esta todo validao, se envia muajjaaj
	return true;
}

//reestablecer contraseñasxd

function restablecerContrasena() {
  var email = prompt("Ingrese su dirección de correo electrónico:");

  if (email == null || email == "") {
      alert("Debe ingresar una dirección de correo electrónico.");
  } else if (!validarEmail(email)) {
      alert("Debe ingresar una dirección de correo electrónico válida.");
  } else {
      alert("Se ha enviado un enlace de restablecimiento de contraseña a su dirección de correo electrónico.");
  }
}

function validarEmail(email) {
  var re = /\S+@\S+\.\S+/;
  return re.test(email);
}

//VALIDACIONES DEL REGISTROMUAJAJJA

function validarRegistro() {
  var nombre = document.getElementById("nombre").value;
  var email = document.getElementById("email").value;
  var password = document.getElementById("password").value;
  var passwordConfirm = document.getElementById("password-confirm").value;
  var errorNombre = document.getElementById("error-nombre");
  var errorEmail = document.getElementById("error-email");
  var errorPassword = document.getElementById("error-password");
  var errorPasswordConfirm = document.getElementById("error-password-confirm");
  
  // Validar que el campo "Nombre completo" no esté vacío
  if (nombre == "") {
    errorNombre.innerHTML = "El campo nombre es obligatorio.";
    return false;
  } else {
    errorNombre.innerHTML = "";
  }
  
  // Validar que el campo "Email" tenga un formato válido
  if (!/\S+@\S+\.\S+/.test(email)) {
    errorEmail.innerHTML = "Ingrese un correo electrónico válido.";
    return false;
  } else {
    errorEmail.innerHTML = "";
  }
  
  // Validar que el campo "Contraseña" tenga al menos 8 caracteres
  if (password.length < 8) {
    errorPassword.innerHTML = "La contraseña debe tener al menos 8 caracteres.";
    return false;
  } else {
    errorPassword.innerHTML = "";
  }
  
  // Validar que los campos "Contraseña" y "Confirmar contraseña" coincidan
  if (password != passwordConfirm) {
    errorPasswordConfirm.innerHTML = "Las contraseñas no coinciden.";
    return false;
  } else {
    errorPasswordConfirm.innerHTML = "";
  }
  
  // Si todas las validaciones pasan, se envía el formulario
  return true;
}
