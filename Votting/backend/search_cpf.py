import requests

def buscar_pessoa_por_cpf(cpf):
    # Defina a URL base da API
    base_url = "http://django-server-production-f3c5.up.railway.app/pessoas/pesquisar_cpf/"
    
    # Defina os parâmetros da requisição
    params = {'cpf': cpf}
    
    try:
        # Faça a requisição GET para a API
        response = requests.get(base_url, params=params)
        
        # Verifique se a requisição foi bem-sucedida (status code 200)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx
        
        # Retorna a resposta JSON como dicionário Python
        return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Exibe o erro HTTP
    except Exception as err:
        print(f"Other error occurred: {err}")  # Exibe outros erros
    return None  # Retorna None em caso de erro
