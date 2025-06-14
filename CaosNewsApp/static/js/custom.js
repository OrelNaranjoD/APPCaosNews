document.addEventListener('DOMContentLoaded', function () {
  function handleFormSubmission(event, formId, messageContainerId) {
    event.preventDefault()

    let form = document.getElementById(formId)
    let formData = new FormData(form)
    let messageContainer = document.getElementById(messageContainerId)

    clearMessages(messageContainer)

    console.log(`Enviando solicitud de ${formId}...`)

    fetch(form.action, {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(`Respuesta recibida (${formId}):`, data)

        if (data.valid) {
          showMessage(messageContainer, 'success', data.success_message)
          setTimeout(() => {
            location.reload()
          }, 4000)
        } else if (data.error_message) {
          showMessage(messageContainer, 'danger', data.error_message)
        }
      })
      .catch(() => {
        showMessage(messageContainer, 'danger', 'Ocurrió un error. Inténtalo de nuevo más tarde.')
      })
  }

  function showMessage(container, type, text) {
    let message = document.createElement('div')
    message.classList.add('alert', `alert-${type}`, 'text-center', 'fade-message')
    message.textContent = text
    container.appendChild(message)
    setTimeout(() => {
      message.style.opacity = '0'
    }, 2000)
    setTimeout(() => {
      message.remove()
    }, 2500)
  }

  function clearMessages(container) {
    container.innerHTML = ''
  }

  // Verificar que los elementos existen antes de agregar event listeners
  const loginForm = document.getElementById('loginForm')
  if (loginForm) {
    loginForm.addEventListener('submit', function (event) {
      handleFormSubmission(event, 'loginForm', 'messageContainer')
    })
  }

  const registerForm = document.getElementById('registerForm')
  if (registerForm) {
    registerForm.addEventListener('submit', function (event) {
      handleFormSubmission(event, 'registerForm', 'registerErrorContainer')
    })
  }
})

/* ********* Obtener fecha actual ********* */
function getFecha() {
  const Month = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
  const Day = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
  const date = new Date()

  const dateElement = document.getElementById('current_date')
  if (dateElement) {
    dateElement.innerHTML = Day[date.getDay()] + ' ' + date.getDate() + ' de ' + Month[date.getMonth()] + ' de ' + date.getFullYear()
  } else {
    console.error('Elemento current_date no encontrado')
  }
}

document.addEventListener('DOMContentLoaded', function () {
  // Obtener referencias a los elementos del formulario
  var form = document.getElementById('contact-form')
  var nombreInput = document.getElementById('nombre')
  var correoInput = document.getElementById('correo')
  var telefonoInput = document.getElementById('telefono')
  var mensajeInput = document.getElementById('mensaje')

  // Verificar si el formulario existe antes de agregar eventos
  if (form && nombreInput && correoInput && telefonoInput && mensajeInput) {
    // Agregar un evento de escucha al enviar el formulario
    form.addEventListener('submit', function (event) {
      // Detener el envío del formulario
      event.preventDefault()

      // Validar los campos del formulario
      var nombreValido = validarNombre()
      var correoValido = validarCorreo()
      var telefonoValido = validarTelefono()
      var mensajeValido = validarMensaje()

      // Verificar si todos los campos son válidos antes de enviar el formulario
      if (nombreValido && correoValido && telefonoValido && mensajeValido) {
        enviarFormulario()
      }
    })
  }

  // Función para validar el campo de nombre
  function validarNombre() {
    var nombre = nombreInput.value.trim()
    var nombreRegExp = /^[a-zA-Z\s]+$/

    if (nombre === '' || !nombreRegExp.test(nombre)) {
      nombreInput.classList.add('is-invalid')
      nombreInput.nextElementSibling.style.display = 'block'
      return false
    } else {
      nombreInput.classList.remove('is-invalid')
      nombreInput.nextElementSibling.style.display = 'none'
      return true
    }
  }

  // Función para validar el campo de correo electrónico
  function validarCorreo() {
    var correo = correoInput.value.trim()
    var correoRegExp = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    if (correo === '' || !correoRegExp.test(correo)) {
      correoInput.classList.add('is-invalid')
      correoInput.nextElementSibling.style.display = 'block'
      return false
    } else {
      correoInput.classList.remove('is-invalid')
      correoInput.nextElementSibling.style.display = 'none'
      return true
    }
  }

  // Función para validar el campo de número de teléfono
  function validarTelefono() {
    var telefono = telefonoInput.value.trim()
    var telefonoRegExp = /^\d+$/

    if (telefono === '' || !telefonoRegExp.test(telefono)) {
      telefonoInput.classList.add('is-invalid')
      telefonoInput.nextElementSibling.style.display = 'block'
      return false
    } else {
      telefonoInput.classList.remove('is-invalid')
      telefonoInput.nextElementSibling.style.display = 'none'
      return true
    }
  }

  // Función para validar el campo de mensaje
  function validarMensaje() {
    if (mensajeInput.value.trim() === '') {
      mensajeInput.classList.add('is-invalid')
      mensajeInput.nextElementSibling.style.display = 'block'
      return false
    } else {
      mensajeInput.classList.remove('is-invalid')
      mensajeInput.nextElementSibling.style.display = 'none'
      return true
    }
  }

  // Función para enviar el formulario
  function enviarFormulario() {
    // Mostrar la ventana emergente de éxito
    var successModal = document.getElementById('success-modal')
    if (successModal) {
      var modal = new bootstrap.Modal(successModal)
      modal.show()
    }

    // Reiniciar el formulario
    if (form) {
      form.reset()
    }
  }
})

//VALIDACIONES PARA EL LOGIN //

function validarEmail(email) {
  // Expresión regular para validar el formato del correo electrónico
  var re = /\S+@\S+\.\S+/
  return re.test(email)
}

function validarlogin() {
  var emailElement = document.getElementById('email')
  var passwordElement = document.getElementById('password')

  // Verificar que los elementos existan
  if (!emailElement || !passwordElement) {
    return false
  }

  var email = emailElement.value
  var password = passwordElement.value

  // Validar que el correo electrónico no esté vacío
  if (email == '') {
    alert('El campo de correo electrónico no puede estar vacío.')
    return false
  }

  // Validar el formato del correo electrónico
  if (!validarEmail(email)) {
    alert('El correo electrónico ingresado no es válido.')
    return false
  }

  // Validar que la contraseña no esté vacía
  if (password == '') {
    alert('El campo de contraseña no puede estar vacío.')
    return false
  }

  // si esta todo validao, se enviará el formulario
  return true
}

//reestablecer contraseñas

function restablecerContrasena() {
  var email = prompt('Ingrese su dirección de correo electrónico:')

  if (email == null || email == '') {
    alert('Debe ingresar una dirección de correo electrónico.')
  } else if (!validarEmail(email)) {
    alert('Debe ingresar una dirección de correo electrónico válida.')
  } else {
    alert('Se ha enviado un enlace de restablecimiento de contraseña a su dirección de correo electrónico.')
  }
}

function validarEmail(email) {
  var re = /\S+@\S+\.\S+/
  return re.test(email)
}

//VALIDACIONES DEL REGISTRO

function validarRegistro() {
  var nombreElement = document.getElementById('nombre')
  var emailElement = document.getElementById('email')
  var passwordElement = document.getElementById('password')
  var passwordConfirmElement = document.getElementById('password-confirm')
  var errorNombre = document.getElementById('error-nombre')
  var errorEmail = document.getElementById('error-email')
  var errorPassword = document.getElementById('error-password')
  var errorPasswordConfirm = document.getElementById('error-password-confirm')

  // Verificar que los elementos principales existan
  if (!nombreElement || !emailElement || !passwordElement || !passwordConfirmElement) {
    return false
  }

  var nombre = nombreElement.value
  var email = emailElement.value
  var password = passwordElement.value
  var passwordConfirm = passwordConfirmElement.value

  // Validar que el campo "Nombre completo" no esté vacío
  if (nombre == '') {
    if (errorNombre) errorNombre.innerHTML = 'El campo nombre es obligatorio.'
    return false
  } else {
    if (errorNombre) errorNombre.innerHTML = ''
  }

  // Validar que el campo "Email" tenga un formato válido
  if (!/\S+@\S+\.\S+/.test(email)) {
    if (errorEmail) errorEmail.innerHTML = 'Ingrese un correo electrónico válido.'
    return false
  } else {
    if (errorEmail) errorEmail.innerHTML = ''
  }

  // Validar que el campo "Contraseña" tenga al menos 8 caracteres
  if (password.length < 8) {
    if (errorPassword) errorPassword.innerHTML = 'La contraseña debe tener al menos 8 caracteres.'
    return false
  } else {
    if (errorPassword) errorPassword.innerHTML = ''
  }

  // Validar que los campos "Contraseña" y "Confirmar contraseña" coincidan
  if (password != passwordConfirm) {
    if (errorPasswordConfirm) errorPasswordConfirm.innerHTML = 'Las contraseñas no coinciden.'
    return false
  } else {
    if (errorPasswordConfirm) errorPasswordConfirm.innerHTML = ''
  }

  // Si todas las validaciones pasan, se envía el formulario
  return true
}
// Toggle password visibility
document.querySelectorAll('.toggle-password').forEach((button) => {
  button.addEventListener('click', function () {
    let input = this.previousElementSibling
    let icon = this.querySelector('i')

    if (input.type === 'password') {
      input.type = 'text'
      icon.classList.remove('fa-eye')
      icon.classList.add('fa-eye-slash')
    } else {
      input.type = 'password'
      icon.classList.remove('fa-eye-slash')
      icon.classList.add('fa-eye')
    }
  })
})

// Solucionar problemas de accesibilidad con modales
$(document).ready(function () {
  // Manejar eventos de modal para accesibilidad
  $('.modal').on('shown.bs.modal', function () {
    // Remover aria-hidden cuando el modal se muestra
    $(this).removeAttr('aria-hidden')
  })

  $('.modal').on('hidden.bs.modal', function () {
    // Restaurar aria-hidden cuando el modal se oculta
    $(this).attr('aria-hidden', 'true')
  })
})
