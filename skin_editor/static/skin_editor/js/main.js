document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('skinCanvas');
    const ctx = canvas ? canvas.getContext('2d', { willReadFrequently: true }) : null;
    if (ctx) ctx.imageSmoothingEnabled = false;

    const usernameInput = document.getElementById('usernameInput');
    const loadSkinButton = document.getElementById('loadSkinButton');
    const downloadButton = document.getElementById('downloadButton');
    const colorPicker = document.getElementById('colorPicker');
    const resetButton = document.getElementById('resetButton');
    const clearButton = document.getElementById('clearButton');
    const swatches = document.querySelectorAll('.swatch');

    if (!canvas || !ctx || !usernameInput || !loadSkinButton || !downloadButton || !colorPicker) {
        console.error('필수 DOM 요소가 없습니다. ID를 확인하세요.');
        return;
    }

    let isDrawing = false;

    function loadDefaultSkin() {
        if (typeof defaultSkinUrl === 'string' && defaultSkinUrl.length > 0) {
            const img = new Image();
            img.crossOrigin = 'Anonymous';
            img.onload = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            };
            img.onerror = () => {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            };
            img.src = defaultSkinUrl;
        } else {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }

    function clearCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    function getPointerPos(evt) {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const clientX = evt.clientX ?? evt.touches?.[0]?.clientX;
        const clientY = evt.clientY ?? evt.touches?.[0]?.clientY;
        if (clientX === undefined || clientY === undefined) return null;
        return {
            x: Math.floor((clientX - rect.left) * scaleX),
            y: Math.floor((clientY - rect.top) * scaleY)
        };
    }

    function drawPixel(point) {
        if (!point) return;
        const size = 1;
        ctx.fillStyle = colorPicker.value;
        ctx.fillRect(point.x, point.y, size, size);
    }

    function startDraw(evt) {
        evt.preventDefault?.();
        isDrawing = true;
        drawPixel(getPointerPos(evt));
    }
    function moveDraw(evt) {
        if (!isDrawing) return;
        evt.preventDefault?.();
        drawPixel(getPointerPos(evt));
    }
    function endDraw(evt) {
        if (!isDrawing) return;
        isDrawing = false;
        evt?.preventDefault?.();
    }

    canvas.style.touchAction = 'none';
    if (window.PointerEvent) {
        canvas.addEventListener('pointerdown', startDraw);
        canvas.addEventListener('pointermove', moveDraw);
        canvas.addEventListener('pointerup', endDraw);
        canvas.addEventListener('pointercancel', endDraw);
        canvas.addEventListener('pointerleave', endDraw);
    } else {
        canvas.addEventListener('mousedown', startDraw);
        canvas.addEventListener('mousemove', moveDraw);
        ['mouseup', 'mouseleave'].forEach((ev) => canvas.addEventListener(ev, endDraw));
        canvas.addEventListener('touchstart', startDraw, { passive: false });
        canvas.addEventListener('touchmove', moveDraw, { passive: false });
        canvas.addEventListener('touchend', endDraw);
        canvas.addEventListener('touchcancel', endDraw);
    }

    downloadButton.addEventListener('click', () => {
        const dataURL = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.download = 'my_custom_skin.png';
        link.href = dataURL;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    loadSkinButton.addEventListener('click', async () => {
        const username = usernameInput.value.trim();
        if (!username) {
            alert('플레이어 이름을 입력해주세요.');
            return;
        }

        const url = typeof getSkinApiUrlTemplate === 'string'
            ? `${getSkinApiUrlTemplate}?username=${encodeURIComponent(username)}`
            : `/skin-editor/api/get-skin/?username=${encodeURIComponent(username)}`;

        try {
            const response = await fetch(url);
            const data = await response.json();
            if (response.ok && data.skin_url) {
                const img = new Image();
                img.crossOrigin = 'Anonymous';
                img.onload = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                };
                img.onerror = () => alert('스킨 이미지 로드에 실패했습니다.');
                img.src = data.skin_url;
            } else {
                alert(data.error || '스킨을 불러오지 못했습니다.');
            }
        } catch (error) {
            console.error(error);
            alert('스킨을 불러오는 중 오류가 발생했습니다.');
        }
    });

    swatches.forEach((swatch) => {
        swatch.addEventListener('click', () => {
            if (swatch.dataset.color) colorPicker.value = swatch.dataset.color;
        });
    });
    resetButton?.addEventListener('click', loadDefaultSkin);
    clearButton?.addEventListener('click', clearCanvas);

    loadDefaultSkin();
});
