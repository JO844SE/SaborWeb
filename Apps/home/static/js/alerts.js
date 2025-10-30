document.addEventListener('DOMContentLoaded', function() {

    if(typeof djangoMessages !== 'undefined' && djangoMessages.length > 0) {
        djangoMessages.forEach(msg => {
            let iconType = 'info';

            switch(msg.type) {
                case 'success':
                    iconType = 'success';
                    break;
                case 'error':
                    iconType = 'error';
                    break;
                case 'warning':
                    iconType = 'warning';
                    break;
                case 'info':
                    iconType = 'info';
                    break;
                default:
                    iconType = 'question';
            }

            Swal.fire({
                title: iconType === 'success' ? 'Success' : iconType === 'error' ? 'Error' : iconType === 'warning' ? 'Warning' : iconType === 'info' ? 'Information' : 'Notice',
                text: msg.text,
                icon: iconType,
                confirmButtonText: 'OK'
            });
        });
    }
});
 