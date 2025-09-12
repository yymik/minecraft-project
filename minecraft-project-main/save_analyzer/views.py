# save_analyzer/views.py

from django.shortcuts import render
from .analyzer_logic import analyze_advancements_from_content

def upload_and_analyze_page(request):
    context = {}

    if request.method == 'POST':
        uploaded_file = request.FILES.get('advancement_file')

        if uploaded_file:
            if not uploaded_file.name.endswith('.json'):
                context['error'] = 'JSON 파일(.json)만 업로드할 수 있습니다.'
            else:
                try:
                    json_content_str = uploaded_file.read().decode('utf-8')
                    analysis_results = analyze_advancements_from_content(json_content_str)
                    
                    if analysis_results.get('error'):
                         # 분석 로직 자체에서 에러를 반환한 경우
                        context['error'] = analysis_results['error']
                    else:
                        # 성공적으로 분석된 경우
                        context['analysis_results'] = analysis_results

                except Exception as e:
                    context['error'] = f'파일을 처리하는 중 오류가 발생했습니다: {e}'
        else:
            context['error'] = '분석할 파일을 선택해주세요.'
            
    return render(request, 'save_analyzer/analyzer_page.html', context)