# Filtros próprios para Wikipedia

**Filtros presentes:**
* Pastor juvanir (/pastor/i /juvanir/i)
* IPs (v4/v6)
* Emails
* Inserção de links de spotify
* Texto em outras línguas


## Como adicionar mais filtros?
Adicione-os em (filters.json)[./filters.json], no seguinte formato:
```json
"nome": {
    "exempt_group": "grupo-que-será-isento",
    "flags": "i",
    "match_all": true,
    "patterns": [
        "pattern_regex_1",
        "pattern_regex_2"
    ],
    "namespace": [0,1,2,3]
}
```
* exempt_group: Qualquer grupo, como confirmed, extendedconfirmed ou autoreviewer;
* flags: i para ignorar maiúscula ou minúscula;
* match_all: Se true, todos os patterns tem que pegar, se false, apenas um basta;
* patterns: Os patterns em regex (crie-os em (regex101.com)[regex101.com]);
* namespace (opcional): Quais namespaces o filtro pega, se for omitido pega em todos. Veja uma lista em (WP:Domínio)[https://pt.wikipedia.org/wiki/Wikipédia:Domínio].