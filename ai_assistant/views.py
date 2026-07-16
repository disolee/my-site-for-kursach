from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

def ask_ollama(prompt):
    """Отправка запроса к локальной Llama"""
    try:    
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7}
        }, timeout=60)
        if response.status_code == 200:
            return response.json()["response"]
        return f"Ollama error: {response.status_code}"
    except Exception as e:
        return f"Сервис временно недоступен. Ошибка: {str(e)}"

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        
        system_prompt = """Ты — AI-помощник интернет-магазина. 
        Твоя задача: вежливо отвечать на вопросы пользователей о товарах, помогать с навигацией по сайту, объяснять, как оформить заказ или вернуть товар. 
        Отвечай кратко и по делу. Если не знаешь ответа — предложи связаться с оператором.
        Пользователь спрашивает: """
        
        full_prompt = system_prompt + user_message
        ai_response = ask_ollama(full_prompt)
        return JsonResponse({'response': ai_response})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def feedback_api(request):
    try:
        data = json.loads(request.body)
        feedback_text = data.get('text', '')
        
        analysis_prompt = f"""Проанализируй следующий отзыв о магазине. 
        Определи тональность: 'positive' (положительный), 'negative' (отрицательный) или 'neutral' (нейтральный). 
        Ответь в формате JSON: {{"sentiment": "positive", "message": "короткое сообщение для пользователя"}}
        
        Отзыв: "{feedback_text}" """
        
        analysis_result = ask_ollama(analysis_prompt)
        
        try:
            start = analysis_result.find('{')
            end = analysis_result.rfind('}') + 1
            if start != -1 and end != 0:
                result_dict = json.loads(analysis_result[start:end])
                sentiment = result_dict.get('sentiment', 'neutral')
                user_message = result_dict.get('message', 'Спасибо за отзыв!')
            else:
                if 'positive' in analysis_result.lower():
                    sentiment = 'positive'
                    user_message = 'Благодарим за положительный отзыв! Мы рады, что вам у нас нравится.'
                elif 'negative' in analysis_result.lower():
                    sentiment = 'negative'
                    user_message = 'Сожалеем, что у вас осталось такое впечатление. Мы передадим отзыв руководству, чтобы исправить ситуацию.'
                else:
                    sentiment = 'neutral'
                    user_message = 'Спасибо, что поделились мнением!'
        except:
            sentiment = 'neutral'
            user_message = 'Спасибо за отзыв!'
            
        return JsonResponse({
            'sentiment': sentiment,
            'message': user_message
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)