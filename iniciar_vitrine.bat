@echo off
title Servidor Vitrine EMCCAMP - Gerente Oriax
cd /d "D:\Projects Python\Vitrine"

:: Inicia o servidor web local (Caddy) em segundo plano
start /B caddy.exe run --config Caddyfile

:: Inicia o Streamlit sem abrir a janela padrão na porta 8501
start /B streamlit run vitrine.py --server.port 8501 --server.headless true

:: Aguarda 3 segundos e abre o navegador direto no dominio personalizado
timeout /t 3 /nobreak > nul
start http://www.oriax.crc