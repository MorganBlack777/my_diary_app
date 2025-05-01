// Confirmation dialog for delete actions
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.btn-delete');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить эту запись?')) {
                e.preventDefault();
            }
        });
    });
});

// Automatically resize textareas based on content
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea.auto-resize');
    
    function autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    }
    
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            autoResize(this);
        });
        
        // Initial resize
        autoResize(textarea);
    });
});
