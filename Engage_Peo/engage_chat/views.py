from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services.gemini_service import get_services_info

def chat_page(request):
    """Render the chatbot UI page."""
    return render(request, "engage_chat/chat.html")


@csrf_exempt  # Remove in production, or handle CSRF properly
def services_query(request):
    """Handle chat requests from frontend."""
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:  # GET fallback for quick browser testing
        data = request.GET

    query = data.get("q") or data.get("message") or ""
    if not query.strip():
        return JsonResponse({"answer": "Please type a question."}, status=400)

    try:
        answer = get_services_info(query)
    except Exception as e:
        return JsonResponse({"answer": f"Error: {str(e)}"}, status=500)

    # Only return the clean answer to frontend
    return JsonResponse({"answer": answer})
