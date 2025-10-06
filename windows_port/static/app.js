document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');

    if (!dropzone || !fileInput || !fileList) {
        return;
    }

    const highlight = () => dropzone.classList.add('dragover');
    const unhighlight = () => dropzone.classList.remove('dragover');

    const renderFiles = (files) => {
        fileList.innerHTML = '';
        if (!files || !files.length) {
            return;
        }
        Array.from(files).forEach((file) => {
            const item = document.createElement('li');
            const name = document.createElement('span');
            name.textContent = file.name;
            const size = document.createElement('span');
            size.textContent = formatBytes(file.size);
            item.appendChild(name);
            item.appendChild(size);
            fileList.appendChild(item);
        });
    };

    const formatBytes = (bytes) => {
        if (!bytes) return '0 B';
        const units = ['B', 'KB', 'MB', 'GB'];
        const power = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
        const sized = bytes / Math.pow(1024, power);
        return `${sized.toFixed(power === 0 ? 0 : 1)} ${units[power]}`;
    };

    const syncFiles = (files) => {
        const dataTransfer = new DataTransfer();
        Array.from(files).forEach((file) => {
            if (file.type.startsWith('image/')) {
                dataTransfer.items.add(file);
            }
        });
        fileInput.files = dataTransfer.files;
        renderFiles(fileInput.files);
    };

    dropzone.addEventListener('dragover', (event) => {
        event.preventDefault();
        highlight();
    });

    ['dragleave', 'dragend'].forEach((type) => {
        dropzone.addEventListener(type, (event) => {
            event.preventDefault();
            unhighlight();
        });
    });

    dropzone.addEventListener('drop', (event) => {
        event.preventDefault();
        unhighlight();
        if (event.dataTransfer?.files?.length) {
            syncFiles(event.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', (event) => {
        renderFiles(event.target.files);
    });
});
