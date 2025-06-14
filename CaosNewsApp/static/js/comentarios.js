/**
 * Sistema de Comentarios - JavaScript
 * Maneja la interactividad del sistema de comentarios
 */

class ComentariosManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initCharacterCount();
    }

    bindEvents() {
        // Formulario principal de comentarios
        $(document).on('submit', '.comentario-form', this.handleComentarioSubmit.bind(this));

        // Formularios de respuesta
        $(document).on('submit', '.respuesta-form-element', this.handleRespuestaSubmit.bind(this));

        // Botones de responder
        $(document).on('click', '.responder-btn', this.toggleRespuestaForm.bind(this));

        // Botones de cancelar respuesta
        $(document).on('click', '.cancelar-respuesta', this.cancelarRespuesta.bind(this));

        // Botones de eliminar comentario
        $(document).on('click', '.eliminar-comentario', this.eliminarComentario.bind(this));

        // Paginación de comentarios
        $(document).on('click', '.comentarios-page-link', this.handlePaginacion.bind(this));

        // Botón de limpiar comentario
        $(document).on('click', '#limpiar-comentario', this.limpiarComentario.bind(this));

        // Contador de caracteres
        $(document).on('input', 'textarea[name="contenido"]', this.updateCharacterCount.bind(this));
    }

    initCharacterCount() {
        // Inicializar contador de caracteres para textareas existentes
        $('textarea[name="contenido"]').each((index, element) => {
            this.updateCharacterCount({target: element});
        });
    }

    updateCharacterCount(event) {
        const textarea = $(event.target);
        const currentLength = textarea.val().length;
        const maxLength = textarea.attr('maxlength') || 500;

        // Buscar el contador más cercano
        const counter = textarea.closest('form').find('.character-count');
        if (counter.length) {
            counter.text(`${currentLength}/${maxLength} caracteres`);

            // Cambiar color según proximidad al límite
            if (currentLength > maxLength * 0.9) {
                counter.addClass('text-danger').removeClass('text-warning text-muted');
            } else if (currentLength > maxLength * 0.75) {
                counter.addClass('text-warning').removeClass('text-danger text-muted');
            } else {
                counter.addClass('text-muted').removeClass('text-danger text-warning');
            }
        }
    }

    handleComentarioSubmit(event) {
        event.preventDefault();

        const form = $(event.target);
        const submitBtn = form.find('button[type="submit"]');
        const formData = new FormData(form[0]);

        // Deshabilitar botón y mostrar loading
        submitBtn.prop('disabled', true).html('<i class="fa-solid fa-spinner fa-spin me-1"></i>Enviando...');

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: (response) => {
                if (response.success) {
                    this.showMessage('success', response.message);
                    form[0].reset();
                    this.updateCharacterCount({target: form.find('textarea[name="contenido"]')[0]});
                    this.recargarComentarios();
                } else {
                    this.showMessage('error', response.error || 'Error al enviar comentario');
                }
            },
            error: (xhr) => {
                const response = xhr.responseJSON;
                if (response && response.errors) {
                    this.showFormErrors(form, response.errors);
                } else {
                    this.showMessage('error', 'Error al enviar comentario. Inténtalo de nuevo.');
                }
            },
            complete: () => {
                submitBtn.prop('disabled', false).html('<i class="fa-solid fa-paper-plane me-1"></i>Comentar');
            }
        });
    }

    handleRespuestaSubmit(event) {
        event.preventDefault();

        const form = $(event.target);
        const submitBtn = form.find('button[type="submit"]');
        const formData = new FormData(form[0]);

        submitBtn.prop('disabled', true).html('<i class="fa-solid fa-spinner fa-spin me-1"></i>Enviando...');

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: (response) => {
                if (response.success) {
                    this.showMessage('success', response.message);
                    form.closest('.respuesta-form-container').hide();
                    form[0].reset();
                    this.recargarComentarios();
                } else {
                    this.showMessage('error', response.error || 'Error al enviar respuesta');
                }
            },
            error: (xhr) => {
                const response = xhr.responseJSON;
                this.showMessage('error', response?.error || 'Error al enviar respuesta');
            },
            complete: () => {
                submitBtn.prop('disabled', false).html('<i class="fa-solid fa-reply me-1"></i>Responder');
            }
        });
    }

    toggleRespuestaForm(event) {
        event.preventDefault();

        const btn = $(event.target).closest('.responder-btn');
        const comentarioId = btn.data('comentario-id');
        const formContainer = $(`#respuesta-form-${comentarioId}`);

        // Ocultar otros formularios de respuesta abiertos
        $('.respuesta-form-container').not(formContainer).hide();

        // Toggle del formulario actual
        formContainer.toggle();

        // Focus en el textarea si se abre
        if (formContainer.is(':visible')) {
            formContainer.find('textarea').focus();
        }
    }

    cancelarRespuesta(event) {
        event.preventDefault();

        const btn = $(event.target);
        const formContainer = btn.closest('.respuesta-form-container');

        // Limpiar y ocultar el formulario
        formContainer.find('form')[0].reset();
        formContainer.hide();
    }

    eliminarComentario(event) {
        event.preventDefault();

        const btn = $(event.target).closest('.eliminar-comentario');
        const comentarioId = btn.data('comentario-id');

        // Confirmar eliminación
        if (!confirm('¿Estás seguro de que deseas eliminar este comentario?')) {
            return;
        }

        btn.prop('disabled', true).html('<i class="fa-solid fa-spinner fa-spin"></i>');

        $.ajax({
            url: `/comentarios/eliminar/${comentarioId}/`,
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: (response) => {
                if (response.success) {
                    this.showMessage('success', response.message);
                    this.recargarComentarios();
                } else {
                    this.showMessage('error', response.error || 'Error al eliminar comentario');
                }
            },
            error: (xhr) => {
                const response = xhr.responseJSON;
                this.showMessage('error', response?.error || 'Error al eliminar comentario');
            },
            complete: () => {
                btn.prop('disabled', false).html('<i class="fa-solid fa-trash fa-sm"></i>');
            }
        });
    }

    handlePaginacion(event) {
        event.preventDefault();

        const link = $(event.target).closest('.comentarios-page-link');
        const page = link.data('page');
        const noticiaId = this.getNoticiaId();

        if (!noticiaId) return;

        $.ajax({
            url: `/comentarios/obtener/${noticiaId}/`,
            method: 'GET',
            data: { page: page },
            success: (response) => {
                if (response.success) {
                    $('#comentarios-lista').html(response.html);

                    // Actualizar paginación si existe
                    if (response.total_pages > 1) {
                        // La paginación se actualiza con el HTML recibido
                        this.scrollToComentarios();
                    }
                }
            },
            error: () => {
                this.showMessage('error', 'Error al cargar comentarios');
            }
        });
    }

    limpiarComentario(event) {
        event.preventDefault();

        const form = $(event.target).closest('form');
        form[0].reset();
        this.updateCharacterCount({target: form.find('textarea[name="contenido"]')[0]});
        this.hideMessages(form);
    }

    recargarComentarios() {
        const noticiaId = this.getNoticiaId();
        if (!noticiaId) return;

        $.ajax({
            url: `/comentarios/obtener/${noticiaId}/`,
            method: 'GET',
            success: (response) => {
                if (response.success) {
                    $('#comentarios-lista').html(response.html);
                    this.scrollToComentarios();
                }
            },
            error: () => {
                console.error('Error al recargar comentarios');
            }
        });
    }

    getNoticiaId() {
        // Obtener ID de la noticia desde el formulario o URL
        const form = $('.comentario-form');
        if (form.length) {
            const action = form.attr('action');
            const match = action.match(/\/comentarios\/crear\/(\d+)\//);
            return match ? match[1] : null;
        }
        return null;
    }

    scrollToComentarios() {
        const comentariosSection = $('#comentarios-section');
        if (comentariosSection.length) {
            $('html, body').animate({
                scrollTop: comentariosSection.offset().top - 100
            }, 500);
        }
    }

    showMessage(type, message) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';

        const messageHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <i class="fa-solid ${icon} me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Mostrar mensaje en la parte superior de la sección de comentarios
        const container = $('#comentarios-section .card-body');
        container.prepend(messageHtml);

        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            container.find('.alert').alert('close');
        }, 5000);
    }

    showFormErrors(form, errors) {
        const messageContainer = form.find('.comentario-messages');
        let errorHtml = '<ul class="mb-0">';

        for (const [field, fieldErrors] of Object.entries(errors)) {
            for (const error of fieldErrors) {
                errorHtml += `<li>${error}</li>`;
            }
        }
        errorHtml += '</ul>';

        messageContainer.html(errorHtml)
                        .removeClass('success')
                        .addClass('error')
                        .show();
    }

    hideMessages(form) {
        form.find('.comentario-messages').hide();
    }
}

// Inicializar cuando el documento esté listo
$(document).ready(function() {
    new ComentariosManager();
});
