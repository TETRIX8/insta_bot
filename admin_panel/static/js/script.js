// Основные скрипты для админ-панели
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всплывающих подсказок
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
                e.preventDefault();
            }
        });
    });

    // Автоматическое скрытие уведомлений
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Обработка выбора шаблона комментария
    const commentSelect = document.getElementById('comment_id');
    const customTextArea = document.getElementById('custom_text');
    
    if (commentSelect && customTextArea) {
        commentSelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                customTextArea.classList.remove('d-none');
                customTextArea.setAttribute('required', 'required');
            } else {
                customTextArea.classList.add('d-none');
                customTextArea.removeAttribute('required');
            }
        });
    }
});
