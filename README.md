# faciflux_erpnext_connector

Conector versionado ERPNext → FluxOS, com outbox transacional e entrega HTTP autenticada por HMAC.

## Implantação Docker

Todos os processos Frappe devem usar a mesma imagem que contém esta app. Use
`Dockerfile.frappe` como build context da própria app; não instale a app em um
container já em execução, pois workers e scheduler possuem sistemas de arquivos
independentes. Após a imagem ser iniciada, execute `bench --site <site> install-app
faciflux_erpnext_connector` (quando ainda não instalada) e `bench --site <site>
migrate` antes de liberar o tráfego.
