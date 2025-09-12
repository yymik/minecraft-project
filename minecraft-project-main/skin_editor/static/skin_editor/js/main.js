document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('skinCanvas');
    const ctx = canvas.getContext('2d', { willReadFrequently: true }); // willReadFrequently 최적화 힌트

    const usernameInput = document.getElementById('usernameInput');
    const loadSkinButton = document.getElementById('loadSkinButton');
    const downloadButton = document.getElementById('downloadButton');
    const colorPicker = document.getElementById('colorPicker');

    let skinViewer; // skinview3d 인스턴스

    // --- DOM 요소 확인 ---
    if (!canvas || !usernameInput || !loadSkinButton || !downloadButton || !colorPicker) {
        console.error("하나 이상의 필수 DOM 요소를 찾을 수 없습니다. ID를 확인하세요.");
        return; // 필수 요소가 없으면 실행 중지
    }

    // 1. 3D 미리보기 초기화
    function initSkinViewer() {
    console.log("Attempting to initialize 3D skin viewer...");
    const skinPreviewElement = document.getElementById('skinPreview');
    if (!skinPreviewElement) {
        console.error("Skin preview DOM 요소를 찾을 수 없습니다 ('skinPreview').");
        return;
    }
    console.log("skinview3d object:", typeof skinview3d, skinview3d);
    console.log("skinPreviewElement dimensions:", skinPreviewElement.clientWidth, skinPreviewElement.clientHeight);

    try {
        skinViewer = new skinview3d.SkinViewer({
            domElement: skinPreviewElement,
            width: skinPreviewElement.clientWidth || 250,
            height: skinPreviewElement.clientHeight || 300,
            animation: new skinview3d.IdleAnimation()
            // skinUrl: canvas.toDataURL() // <<-- 이 부분을 일단 주석 처리 또는 삭제
        });
        console.log("SkinViewer instance created (without initial skinUrl):", skinViewer);

        window.addEventListener('resize', () => {
            if (skinViewer && skinPreviewElement.parentElement) {
                skinViewer.width = skinPreviewElement.clientWidth;
                skinViewer.height = skinPreviewElement.clientHeight;
            }
        });
    } catch (error) {
        console.error("skinview3d 초기화 중 명시적 오류 발생:", error);
        if (skinPreviewElement) {
            skinPreviewElement.innerHTML = "<p>3D 미리보기를 로드할 수 없습니다...</p>";
        }
    }
    }


    // 2. 캔버스 내용으로 3D 미리보기 업데이트
    function updatePreview() {
    if (skinViewer) {
        try {
            const dataUrl = canvas.toDataURL('image/png');
            console.log("Updating 3D preview with canvas data URL (first 50 chars):", dataUrl.substring(0, 50)); // << 추가
            skinViewer.skinUrl = dataUrl;
        } catch (error) {
            console.error("3D 미리보기 업데이트 중 toDataURL 오류:", error);
        }
    } else {
        console.log("skinViewer not initialized, cannot update 3D preview."); // << 추가
    }
    }

    // 3. 기본 스킨 (또는 빈 캔버스) 로드
    function loadDefaultSkin() {
        // 템플릿에서 전달된 기본 스킨 URL 사용 (없으면 빈 캔버스)
        // editor.html에서 <script>var defaultSkinUrl = "{% static 'skin_editor/assets/images/default_skin.png' %}";</script> 와 같이 설정해야 함
        if (typeof defaultSkinUrl !== 'undefined' && defaultSkinUrl) {
            const defaultSkinImg = new Image();
            defaultSkinImg.crossOrigin = "Anonymous"; // 로컬 파일은 필요 없지만, 일관성 유지
            defaultSkinImg.onload = () => {
                console.log("Default skin image loaded successfully into 2D canvas."); // << 추가
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.drawImage(defaultSkinImg, 0, 0, canvas.width, canvas.height);
                updatePreview();
            };
            defaultSkinImg.onerror = () => {
                console.error("기본 스킨 이미지 로드 실패:", defaultSkinUrl, "빈 캔버스로 시작합니다.");
                console.warn("기본 스킨 이미지 로드 실패:", defaultSkinUrl, "빈 캔버스로 시작합니다.");
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                updatePreview();
            };
            defaultSkinImg.src = defaultSkinUrl;
        } else {
            console.log("기본 스킨 URL이 제공되지 않았습니다. 빈 캔버스로 시작합니다.");
            ctx.clearRect(0, 0, canvas.width, canvas.height); // 빈 캔버스
            updatePreview();
        }
    }

    // 4. 캔버스에 그리기 로직
    let isDrawing = false;

    function getMousePos(canvasEl, evt) {
        const rect = canvasEl.getBoundingClientRect();
        // 캔버스의 실제 해상도에 맞게 좌표 스케일링
        const scaleX = canvasEl.width / rect.width;
        const scaleY = canvasEl.height / rect.height;
        return {
            x: Math.floor((evt.clientX - rect.left) * scaleX),
            y: Math.floor((evt.clientY - rect.top) * scaleY)
        };
    }

    canvas.addEventListener('mousedown', (e) => {
        if (e.button !== 0) return; // 왼쪽 마우스 버튼만 허용
        isDrawing = true;
        const pos = getMousePos(canvas, e);
        drawPixel(pos.x, pos.y);
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDrawing) {
            const pos = getMousePos(canvas, e);
            drawPixel(pos.x, pos.y);
        }
    });

    function stopDrawing() {
        if (isDrawing) {
            isDrawing = false;
            updatePreview(); // 그리기 완료 후 미리보기 업데이트
        }
    }
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseleave', stopDrawing); // 캔버스 밖으로 나가면 그리기 중지

    function drawPixel(x, y) {
        if (x >= 0 && x < canvas.width && y >= 0 && y < canvas.height) { // 캔버스 범위 내에서만 그리기
            ctx.fillStyle = colorPicker.value;
            ctx.fillRect(x, y, 1, 1); // 1x1 픽셀
        }
        // mousemove 시마다 updatePreview()를 호출하면 성능에 영향을 줄 수 있으므로,
        // mouseup/mouseleave 시에만 호출하도록 변경했습니다.
    }

    // 5. 스킨 다운로드 로직
    downloadButton.addEventListener('click', () => {
        try {
            const dataURL = canvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.download = 'my_custom_skin.png';
            link.href = dataURL;
            document.body.appendChild(link); // Firefox에서 필요할 수 있음
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error("스킨 다운로드 중 오류:", error);
            alert("스킨을 다운로드하는 중 오류가 발생했습니다.");
        }
    });

    // 6. 플레이어 이름으로 스킨 불러오기 (Django 백엔드 API 호출)
    loadSkinButton.addEventListener('click', async () => {
        const username = usernameInput.value.trim();
        if (!username) {
            alert('플레이어 이름을 입력해주세요.');
            return;
        }

        // Django 백엔드의 API 엔드포인트 호출
        // editor.html에서 <script>var getSkinApiUrl = "{% url 'skin_editor:get_skin_api' %}";</script> 와 같이 설정하고 사용
        let proxyApiUrl;
        if (typeof getSkinApiUrlTemplate !== 'undefined') {
            // URL 템플릿이 있다면 (예: /skin-editor/api/get-skin/?username=PLACEHOLDER)
            // 또는 Django의 {% url %} 태그로 생성된 전체 URL을 사용
            proxyApiUrl = `${getSkinApiUrlTemplate}?username=${encodeURIComponent(username)}`;
        } else {
            // 하드코딩된 경로 (템플릿 변수 설정이 더 좋음)
            console.warn("getSkinApiUrlTemplate 변수가 정의되지 않았습니다. API URL을 하드코딩합니다.");
            proxyApiUrl = `/skin-editor/api/get-skin/?username=${encodeURIComponent(username)}`;
        }


        try {
            const response = await fetch(proxyApiUrl);
            const data = await response.json(); // 응답이 항상 JSON이라고 가정

            if (response.ok && data.skin_url) {
                const skinPngUrl = data.skin_url;
                const img = new Image();
                img.crossOrigin = "Anonymous"; // Mojang 스킨 URL은 CORS 헤더를 포함하는 경우가 많음
                img.onload = () => {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    updatePreview();
                };
                img.onerror = (e) => {
                    console.error("스킨 이미지 로드 오류 (URL에서):", skinPngUrl, e);
                    alert(`스킨 이미지 로드에 실패했습니다 (URL: ${skinPngUrl}). CORS 문제 또는 이미지 URL이 잘못되었을 수 있습니다.`);
                };
                img.src = skinPngUrl;
            } else {
                const errorMessage = data.error || '서버에서 오류 응답을 받았습니다. (상세 정보 없음)';
                console.error("스킨 불러오기 실패 (서버 응답):", errorMessage, data);
                alert(`스킨을 불러오지 못했습니다: ${errorMessage}`);
            }

        } catch (error) {
            console.error('스킨 불러오기 중 네트워크/JSON 파싱 오류:', error);
            alert('스킨을 불러오는 중 네트워크 오류 또는 응답 처리 문제가 발생했습니다. 브라우저 콘솔을 확인해주세요.');
        }
    });

    // --- 초기화 실행 ---
    initSkinViewer();
    loadDefaultSkin(); // 페이지 로드 시 기본 스킨 또는 빈 캔버스 표시
});