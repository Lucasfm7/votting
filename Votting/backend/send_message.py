import requests
import random

def send_sms(to_phone_number):
    # Gerar um código de validação de 6 dígitos
    codigo_validacao = random.randint(100000, 999999)
    
    # Defina a URL base da API
    base_url = "https://django-server-production-f3c5.up.railway.app/send-sms/"
    
    # Defina os parâmetros da requisição
    body = {
        "to_phone_number": to_phone_number,  # Número de telefone destino
        "message_body": f"Seu código de validação é: {codigo_validacao}. Use este código para completar a validação."
    }
    
    try:
        # Faça a requisição POST para a API de envio de SMS
        response = requests.post(base_url, json=body)
        
        # Verifique se a requisição foi bem-sucedida (status code 200)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx
        
        # Retorna o código de validação para uso posterior (como verificação)
        return codigo_validacao
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Exibe o erro HTTP
    except Exception as err:
        print(f"Other error occurred: {err}")  # Exibe outros erros
    return None  # Retorna None em caso de erro
