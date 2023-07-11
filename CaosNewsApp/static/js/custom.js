$(document).ready(function() {
  /* ********* Mensajes Inicio de sesión ********* */
  $('#loginForm').on('submit', function(event) {
      event.preventDefault();
      var form = $(this);
      var errorContainer = $('#errorContainer');
      var emailError = $('#emailError');
      var passwordError = $('#passwordError');

      errorContainer.empty();
      emailError.empty();
      passwordError.empty();

      $.ajax({
          url: form.attr('action'),
          method: 'POST',
          data: form.serialize(),
          success: function(data) {
              if (data.valid) {
                  var successMessage = $('<div id="successAlert" class="alert alert-success text-center">' + data.success_message + '</div>');
                  errorContainer.html(successMessage);
                  setTimeout(function() {
                      successMessage.fadeOut(200, function() {
                          $(this).remove();
                          window.location.href = '/';
                      });
                  }, 500);
              } else {
                  if (data.error_message) {
                      var errorMessage = $('<div class="alert alert-danger text-center">' + data.error_message + '</div>');
                      errorContainer.html(errorMessage);
                  }
              }
          },
          error: function(xhr, textStatus, error) {
              var errorMessage = $('<div class="alert alert-danger text-center">Ocurrió un error en el inicio de sesión. Inténtalo de nuevo más tarde.</div>');
              errorContainer.html(errorMessage);
          }
      });
  });
});


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

document.addEventListener('DOMContentLoaded', function() {
  // Obtener referencias a los elementos del formulario
  var form = document.getElementById('contact-form');
  var nombreInput = document.getElementById('nombre');
  var correoInput = document.getElementById('correo');
  var telefonoInput = document.getElementById('telefono');
  var mensajeInput = document.getElementById('mensaje');

  // Agregar un evento de escucha al enviar el formulario
  form.addEventListener('submit', function (event) {
      // Detener el envío del formulario
      event.preventDefault();

      // Validar los campos del formulario
      var nombreValido = validarNombre();
      var correoValido = validarCorreo();
      var telefonoValido = validarTelefono();
      var mensajeValido = validarMensaje();

      // Verificar si todos los campos son válidos antes de enviar el formulario
      if (nombreValido && correoValido && telefonoValido && mensajeValido) {
          enviarFormulario();
      }
  });

  // Función para validar el campo de nombre
  function validarNombre() {
      var nombre = nombreInput.value.trim();
      var nombreRegExp = /^[a-zA-Z\s]+$/;

      if (nombre === '' || !nombreRegExp.test(nombre)) {
          nombreInput.classList.add('is-invalid');
          nombreInput.nextElementSibling.style.display = 'block';
          return false;
      } else {
          nombreInput.classList.remove('is-invalid');
          nombreInput.nextElementSibling.style.display = 'none';
          return true;
      }
  }

  // Función para validar el campo de correo electrónico
  function validarCorreo() {
      var correo = correoInput.value.trim();
      var correoRegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (correo === '' || !correoRegExp.test(correo)) {
          correoInput.classList.add('is-invalid');
          correoInput.nextElementSibling.style.display = 'block';
          return false;
      } else {
          correoInput.classList.remove('is-invalid');
          correoInput.nextElementSibling.style.display = 'none';
          return true;
      }
  }

  // Función para validar el campo de número de teléfono
  function validarTelefono() {
      var telefono = telefonoInput.value.trim();
      var telefonoRegExp = /^\d+$/;

      if (telefono === '' || !telefonoRegExp.test(telefono)) {
          telefonoInput.classList.add('is-invalid');
          telefonoInput.nextElementSibling.style.display = 'block';
          return false;
      } else {
          telefonoInput.classList.remove('is-invalid');
          telefonoInput.nextElementSibling.style.display = 'none';
          return true;
      }
  }

  // Función para validar el campo de mensaje
  function validarMensaje() {
      if (mensajeInput.value.trim() === '') {
          mensajeInput.classList.add('is-invalid');
          mensajeInput.nextElementSibling.style.display = 'block';
          return false;
      } else {
          mensajeInput.classList.remove('is-invalid');
          mensajeInput.nextElementSibling.style.display = 'none';
          return true;
      }
  }

  // Función para enviar el formulario
  function enviarFormulario() {


      // Mostrar la ventana emergente de éxito
      var successModal = document.getElementById('success-modal');
      var modal = new bootstrap.Modal(successModal);
      modal.show();

      // Reiniciar el formulario
      form.reset();
  }
});


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
