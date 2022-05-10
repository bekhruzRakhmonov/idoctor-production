from django.shortcuts import render

def error_403(request, exception):
	context = {
		"error":exception
	}
	return render(request,"pages/errors.html",context)

def error_404(request, exception):
	context = {
		"error": "Page not found."
	}
	return render(request,"pages/errors.html",context)

def error_500(request):
	exception = "Server not response"
	context = {
		"error":exception
	}
	return render(request,"pages/errors.html",context)